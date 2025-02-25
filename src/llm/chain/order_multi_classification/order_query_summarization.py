import re
import time

from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from loguru import logger
from openai import RateLimitError

from infra.order_classification import WAIT_TIME_IN_SEC
from llm.chain.order_classification_chain import get_llm_by_client_credentials

_PROMPT_TEMPLATE = """
Заявка жильца:
```
{query}
```

Прочитай заявку жильца и убери из неё:
- Срочность (необходимость немедленного решения).
- Агрессию, раздражение, ругательства, оскорбления, угрозы.
Важно, чтобы заявка звучала нейтрально, а не агрессивно или срочно.

Твоей ответ должен содержать только содержание заявки жильца.

Содержание заявки жильца:
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

    # TODO: make decorator for it
    except RateLimitError as e:
        logger.error(f"RateLimit error occurred: {str(e)}")
        logger.info(f"Wait {WAIT_TIME_IN_SEC} seconds and try again")
        time.sleep(WAIT_TIME_IN_SEC)
        logger.info(
            f"Timeout passed, "
            f"try to classify order '{order_query}' "
            f"of client '{client}' again"
        )

        return get_order_query_summary(
            llm=llm,
            order_query=order_query,
            client=client,
            verbose=verbose,
        )


if __name__ == "__main__":
    from infra.llm_clients_credentials import Service

    llm = get_llm_by_client_credentials(service=Service.ORDER_CLASSIFICATION)

    order_query = """
Из-за пожарных учений отрубилась система вентиляции и не включается. СРОЧНО ПРОШУ
ВКЛЮЧИТЬ.
ЗАДЫХАЕМСЯ.
    """

    summary = get_order_query_summary(
        llm=llm,
        order_query=order_query,
    )

    print(f"Order Query: {order_query}")
    print(f"Order Summary: {summary}")
