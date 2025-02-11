import time

from langchain.chains.llm import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from loguru import logger
from openai import RateLimitError

from infra.order_classification import WAIT_TIME_IN_SEC
from scheme.order_classification.order_classification_scheme import (
    MostRelevantClassLLMResponse,
)

_PROMPT_TEMPLATE = """
Заявка: "{query}"

Даны оценки соответствия заявки следующим классам по шкале от 0 до 10:
```
{scores}
```

Вот список классов с правилами, чтобы понять относится ли заявку к тому или иному классу или нет,
также у некоторых классов есть правила, по которым можно понять,
что заявка точно не относится к нему:
```
{rules_by_classes}
```

Выбери класс, который ты считаешь наиболее подходящим для этой заявки.
Основывайся только на списке правил всех классов и ранее данных оценках соответствия.
Поясни свой выбор, ссылаясь на правила и ранее данные оценки соответствия.


Примеры размышлений:
Заявка 1: Дверь на -2 корпуса Афины выгнута в сторону лифтов (винтом) и треснуто стекло
Размышления 1: Поломка двери и окон не подходит под аварийные заявки, тк не перечислена в правилах аварийных заявок. Двери это не инженерные сети, починкой дверей и общем благоустройством дома занимается управляющий дома, поэтому заявка относится к “Другой класс”

Заявка 2: на потолке над парковочным местом протечка
Размышления 2: слово “протечка” причем не просто крана - говорит нам о том что где-то могут быть повреждены трубы. Из заявки этого не понятно, но сначала на место протечки нужно вызвать техника чтобы убедиться что там нет ничего серьезного - поэтому заявка относится к классу “Аварийная”. Заявка может пересекаться с правилами для охраны “все что связано с парковкой”, но охрана с этим вопросом никак не поможет и правило просто пересекается по семантике

Заявка 3: Пахнет гарью! Срочно проверить
Размышления 3: Любая подсказка о том что сейчас идет пожар говорит о том что это аварийная заявка. Эта заявка не просто сообщает о возможности пожара, а она говорит о том что идет пожар уже. Заявка относится к классу “Аварийная”

Заявка 4: Мешок мешает проходу к эвакуационному выходу
Размышления 4: Пожара не наблюдается, хоть и есть угроза опасности жителям. Но тк пожара нет, этой заявкой должны заниматься другие люди. Чтобы решить проблему нужно выкинуть мешок следовательно подходит клининг. Заявка относится к классу “Клининг”

Заявка 5: слабо греют батареи в квартире
Размышления 5: Батареи греют? - да. То что слабо - это уже не относится к инженерным сетям, потому что когда проблема возникает с поломкой бойлера - вода становится совсем холодной. Эта заявка не подходит под класс “Аварийная”, хоть и очень похожа. Заявка относится к классу “Другой класс”


Ответь в формате JSON по схеме:
- "comment": "<твои пояснения>"
- "order_class": "<наиболее подходящий класс из списка>",
"""

parser = JsonOutputParser(pydantic_object=MostRelevantClassLLMResponse)


def _get_prompt() -> PromptTemplate:
    prompt = PromptTemplate(
        input_variables=["scores"],
        template=_PROMPT_TEMPLATE,
    )
    return prompt


def get_most_relevant_class_chain(
    llm: AzureChatOpenAI,
    verbose: bool = False,
) -> LLMChain:
    prompt = _get_prompt()

    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        output_parser=parser,
        verbose=verbose,
    )
    return chain


def get_most_relevant_class(
    llm: AzureChatOpenAI,
    order_query: str,
    rules_by_classes: dict,
    scores: str,
    client: str | None = None,
    verbose: bool = False,
) -> MostRelevantClassLLMResponse:
    try:
        chain = get_most_relevant_class_chain(
            llm=llm,
            verbose=verbose,
        )

        order_class_response: dict = chain.run(
            query=order_query,
            rules_by_classes=rules_by_classes,
            scores=scores,
        )
        order_class = MostRelevantClassLLMResponse(**order_class_response)

        return order_class
    except RateLimitError as e:
        logger.error(f"RateLimit error occurred: {str(e)}")
        logger.info(f"Wait {WAIT_TIME_IN_SEC} seconds and try again")
        time.sleep(WAIT_TIME_IN_SEC)
        logger.info(
            f"Timeout passed, try to classify order '{order_query}' of client '"
            f"{client}' again"
        )

        return get_most_relevant_class(
            llm=llm,
            order_query=order_query,
            rules_by_classes=rules_by_classes,
            scores=scores,
            client=client,
            verbose=verbose,
        )
