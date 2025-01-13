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
{scores}

Вот список классов с правилами,
по которым можно понять относится ли заявку к классу или нет,
также у некоторых классов есть правила, по которым можно понять,
что заявка точно не относится к этому классу:
```
{rules_by_classes}
```

Какой класс ты считаешь наиболее подходящим для этой заявки?
Поясни свой выбор.
Твой ответ должен содержать только наиболее подходящий класс для этой заявки,
на основе правил и оценок,
и объяснение почему именно этот класс самый подходящий.
Основывайся только на правилах классов и ссылайся на них при объяснении.

Ответь в формате JSON по схеме:
- "comment": "<твои пояснения>"
- "order_class": "<наиболее подходящий класс заявки из списка>",
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
