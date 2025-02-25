from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate

from infra.llm_clients_credentials import get_llm_by_client_credentials, Service


def get_order_classification_chain(
    prompt_template: str,
    client: str,
) -> LLMChain:
    llm = get_llm_by_client_credentials(
        client=client,
        service=Service.ORDER_CLASSIFICATION,
    )

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["query"],
    )

    return LLMChain(
        llm=llm,
        prompt=prompt,
    )
