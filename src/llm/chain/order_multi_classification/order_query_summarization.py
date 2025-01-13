import re
import time

from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from loguru import logger
from openai import RateLimitError

from infra.order_classification import WAIT_TIME_IN_SEC

_PROMPT_TEMPLATE = """
Прочитай содержание заявки жильца и суммаризируй её.
 
Убери из заявки упоминания, схожие на:
- Агрессия, раздражение, просьбы о помощи, жалобы, недовольство.
- Срочность (крайний срок, необходимость немедленного решения).
- Личные мнения, оценки, требования, предупреждения, опасения,
  потенциальную опасность.
- Ругательства, оскорбления, угрозы.

Кратко, чётко и точно опиши суть проблемы, которая описана в заявке.
Все требования жильца в заявке описывай, как просьбы жильца.

Заявка жильца: "{query}"

Твоё описание сути проблемы:
"""


def _get_prompt() -> PromptTemplate:
    prompt = PromptTemplate(
        input_variables=["query"],
        template=_PROMPT_TEMPLATE,
    )
    return prompt


def get_summarization_chain(
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


def format_order_query(order_query: str) -> str:
    order_query = re.sub(r"[\s!\n]+", " ", order_query)
    return order_query


def get_order_query_summary(
    llm: AzureChatOpenAI,
    order_query: str,
    client: str | None = None,
    verbose: bool = False,
) -> str:
    try:
        chain = get_summarization_chain(
            llm=llm,
            verbose=verbose,
        )

        order_query = format_order_query(order_query)
        query_summary: str = chain.run(query=order_query)
        return query_summary

    except RateLimitError as e:
        logger.error(f"RateLimit error occurred: {str(e)}")
        logger.info(f"Wait {WAIT_TIME_IN_SEC} seconds and try again")
        time.sleep(WAIT_TIME_IN_SEC)
        logger.info(
            f"Timeout passed, try to classify order '{order_query}' of client "
            f"'{client}' again"
        )

        return get_order_query_summary(
            llm=llm,
            order_query=order_query,
            client=client,
            verbose=verbose,
        )
