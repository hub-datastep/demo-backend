from langchain.chains.llm import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from scheme.order_classification.order_classification_scheme import MostRelevantClassLLMResponse

_PROMPT_TEMPLATE = """
Заявка: "{query}"

Даны оценки соответствия заявки следующим классам:
{scores}

Какой класс вы считаете наиболее подходящим для этой заявки? Поясните свой выбор.
Твой ответ должен содержать только наиболее подходящий класс для этой заявки и объяснение на другой строке.

Ответь в формате JSON по схеме:
- "order_class": "<наиболее подходящий класс заявки из списка>",
- "comment": "<твои пояснения>"
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
    chain: LLMChain,
    order_query: str,
    scores: str,
) -> dict:
    # TODO: add RateLimitError handling
    order_class: dict = chain.run(
        query=order_query,
        scores=scores,
    )
    return order_class
