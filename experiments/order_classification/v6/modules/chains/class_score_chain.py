import time

from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from loguru import logger
from openai import RateLimitError

from order_classification.v6.modules.constants import WAIT_TIME_IN_SEC
from order_classification.v6.modules.utils.order_classification_rules import (
    format_rules_list
)

_PROMPT_TEMPLATE = """
На основе правил оцени на сколько по шкале от 0 до 10 эта заявка относится к этому классу
и поясни свой ответ.

Заявка: "{query}"
Класс: "{class_name}"
Правила, чтобы понять, что заявка относится к этому классу или нет:
```
{rules}
```

Примеры размышлений, для того чтобы тебе проще было делать обоснования:
Заявка 1: Дверь на -2 корпуса Афины выгнута в сторону лифтов (винтом) и треснуто стекло
Размышления 1: Поломка двери и окон не подходит под аварийные заявки, тк не перечислена
в правилах аварийных заявок. Двери это не инженерные сети, починкой дверей и общем
благоустройством дома занимается управляющий дома, поэтому заявка относится к “Другой
класс”

Заявка 2: на потолке над парковочным местом протечка
Размышления 2: слово “протечка” причем не просто крана - говорит нам о том что где-то
могут быть повреждены трубы. Из заявки этого не понятно, но сначала на место протечки
нужно вызвать техника чтобы убедиться что там нет ничего серьезного - поэтому заявка
относится к классу “Аварийная”. Заявка может пересекаться с правилами для охраны “все
что связано с парковкой”, но охрана с этим вопросом никак не поможет и правило просто
пересекается по семантике

Заявка 3: Пахнет гарью! Срочно проверить
Размышления 3: Любая подсказка о том что сейчас идет пожар говорит о том что это
аварийная заявка. Эта заявка не просто сообщает о возможности пожара, а она говорит о
том что идет пожар уже. Заявка относится к классу “Аварийная”

Заявка 4: Мешок мешает проходу к эвакуационному выходу
Размышления 4: Пожара не наблюдается, хоть и есть угроза опасности жителям. Но тк
пожара нет, этой заявкой должны заниматься другие люди. Чтобы решить проблему нужно
выкинуть мешок следовательно подходит клининг. Заявка относится к классу “Клининг”

Заявка 5: слабо греют батареи в квартире
Размышления 5: Батареи греют? - да. То что слабо - это уже не относится к инженерным
сетям, потому что когда проблема возникает с поломкой бойлера - вода становится совсем
холодной. Эта заявка не подходит под класс “Аварийная”, хоть и очень похожа. Заявка
относится к классу “Другой класс”


Твой ответ должен быть в формате:
Класс: <класс заявки>
- Обоснование: <твои пояснения>
- Оценка: <твоя оценка от 0 до 10>
"""


def _get_prompt() -> PromptTemplate:
    prompt = PromptTemplate(
        input_variables=["rules", "query"],
        template=_PROMPT_TEMPLATE,
    )
    return prompt


def get_class_score_chain(
    llm: AzureChatOpenAI,
    verbose: bool = False,
) -> LLMChain:
    prompt = _get_prompt()

    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=verbose,
    )
    return chain


def get_class_score(
    chain: LLMChain,
    order_query: str,
    class_name: str,
    rules: list[str],
    exclusion_rules: list[str] | None = None,
    client: str | None = None,
) -> str:
    try:
        # Combine rules list to str
        rules_str = format_rules_list(rules)

        # If class has exclusion rules, add them to prompt
        if exclusion_rules is not None:
            exclusion_rules_str = format_rules_list(exclusion_rules)
            rules_str += (
                "Правила, по которым можно понять, что заявка точно не относится к "
                "этому классу:"
                f"\n{exclusion_rules_str}"
            )

        score: str = chain.run(
            query=order_query,
            class_name=class_name,
            rules=rules_str,
        )
        return score
    except RateLimitError as e:
        logger.error(f"RateLimit error occurred: {str(e)}")
        logger.info(f"Wait {WAIT_TIME_IN_SEC} seconds and try again")
        time.sleep(WAIT_TIME_IN_SEC)
        logger.info(
            f"Timeout passed, try to classify order '{order_query}' of client '"
            f"{client}' again"
        )

        return get_class_score(
            chain=chain,
            order_query=order_query,
            class_name=class_name,
            rules=rules,
            client=client,
        )
