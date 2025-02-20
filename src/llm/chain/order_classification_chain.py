from fastapi import HTTPException, status
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from infra.env import env
from infra.order_classification_clients_credentials import (
    ORDER_CLASSIFICATION_CLIENTS_CREDENTIALS,
)
from scheme.order_classification.client_credentials_scheme import ClientCredentials
from scheme.order_classification.order_classification_config_scheme import OrderClassificationClient


def _get_client_credentials(client: str) -> ClientCredentials:
    available_clients_list = list(ORDER_CLASSIFICATION_CLIENTS_CREDENTIALS.keys())

    if client not in available_clients_list:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Azure OpenAI Credentials for client '{client}' not found"
        )

    credentials = ClientCredentials(**ORDER_CLASSIFICATION_CLIENTS_CREDENTIALS[client])

    return credentials


def get_llm_by_client_credentials(client: str | None = None) -> AzureChatOpenAI:
    # Create LLM with client Azure OpenAI credentials
    if not env.IS_DEV_ENV or client is not None:
        client_credentials = _get_client_credentials(client)

        llm = AzureChatOpenAI(
            deployment_name=client_credentials.deployment_name,
            openai_api_key=client_credentials.api_key,
            azure_endpoint=client_credentials.endpoint,
            temperature=0,
            verbose=False,
        )
    # Create LLM with development Azure OpenAI credentials
    else:
        llm = AzureChatOpenAI(
            deployment_name=env.AZURE_DEPLOYMENT_NAME_ORDER_CLASSIFICATION,
            temperature=0,
            verbose=False,
        )

    return llm


def get_order_classification_chain(
    prompt_template: str,
    client: str,
) -> LLMChain:
    llm = get_llm_by_client_credentials(client=client)

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["query"],
    )

    return LLMChain(
        llm=llm,
        prompt=prompt,
    )


if __name__ == "__main__":
    a = _get_client_credentials(OrderClassificationClient.VYSOTA)
    print(a)
