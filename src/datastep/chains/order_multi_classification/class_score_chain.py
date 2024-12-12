import time

from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from loguru import logger
from openai import RateLimitError

from infra.order_classification import WAIT_TIME_IN_SEC

_PROMPT_TEMPLATE = """
На основе правил оцени на сколько по шкале от 0 до 10 эта заявка относится к этому классу? 
Поясните свой ответ.

Заявка: "{query}"
Класс: "{class_name}"
Правила для определения относится ли эта заявка к этому классу:
{rules}

Твой ответ должен быть в формате:
Класс: <класс заявки>
- Оценка: <твоя оценка от 0 до 10>
- Обоснование: <твои пояснения>
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
    client: str | None = None,
) -> str:
    try:
        score: str = chain.run(
            query=order_query,
            class_name=class_name,
            rules="\n".join(rules),
        )
        return score
    except RateLimitError as e:
        logger.error(f"RateLimit error occurred: {str(e)}")
        logger.info(f"Wait {WAIT_TIME_IN_SEC} seconds and try again")
        time.sleep(WAIT_TIME_IN_SEC)
        logger.info(
            f"Timeout passed, try to classify order '{order_query}' of client '{client}' again"
        )

        return get_class_score(
            chain=chain,
            order_query=order_query,
            class_name=class_name,
            rules=rules,
            client=client,
        )
