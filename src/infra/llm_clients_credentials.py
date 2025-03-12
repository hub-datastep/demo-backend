from fastapi import HTTPException, status
from langchain_openai import AzureChatOpenAI
from loguru import logger
from scheme.order_classification.client_credentials_scheme import ClientCredentials

from infra.env import env


class Client:
    VYSOTA = "vysota"
    UNISTROY = "unistroy"


class Service:
    ORDER_CLASSIFICATION = "order_classification"
    MAPPING = "mapping"


LLM_CLIENTS_CREDENTIALS = {
    f"{Client.VYSOTA}": {
        "endpoint": env.VYSOTA_AZURE_OPENAI_ENDPOINT,
        "api_key": env.VYSOTA_AZURE_OPENAI_API_KEY,
        "deployment_name": env.VYSOTA_AZURE_DEPLOYMENT_NAME_ORDER_CLASSIFICATION,
    },
    f"{Client.UNISTROY}": {
        "endpoint": env.UNISTROY_AZURE_OPENAI_ENDPOINT,
        "api_key": env.UNISTROY_AZURE_OPENAI_API_KEY,
        "deployment_name": env.UNISTROY_AZURE_DEPLOYMENT_NAME_MAPPING,
    },
}


def _get_client_credentials(client: str) -> ClientCredentials:
    available_clients_list = list(LLM_CLIENTS_CREDENTIALS.keys())

    # Check if client has credentials
    if client not in available_clients_list:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Azure OpenAI Credentials for client '{client}' not found",
        )

    credentials = ClientCredentials(**LLM_CLIENTS_CREDENTIALS[client])
    logger.info(f"LLM Credentials: using '{client}' client Azure OpenAI Credentials")

    return credentials


def _get_default_deployment_by_service(
    service: str | None = None,
) -> str | None:
    """
    Получает название деплоймента по сервису, которые мы предоставляем.
    """

    deployment_name = None

    if service == Service.ORDER_CLASSIFICATION:
        deployment_name = env.AZURE_DEPLOYMENT_NAME_ORDER_CLASSIFICATION
    elif service == Service.MAPPING:
        deployment_name = env.AZURE_DEPLOYMENT_NAME_MAPPING

    logger.info(
        f"LLM Credentials: using default Azure OpenAI Credentials (deployment: '{deployment_name}')"
    )

    return deployment_name


def get_llm_by_client_credentials(
    client: str | None = None,
    service: str | None = None,
) -> AzureChatOpenAI:
    # Create LLM with client Azure OpenAI credentials
    if not env.IS_DEV_ENV or client is not None:
        client_credentials = _get_client_credentials(client)

        llm = AzureChatOpenAI(
            azure_deployment=client_credentials.deployment_name,
            api_key=client_credentials.api_key,
            azure_endpoint=client_credentials.endpoint,
            temperature=0,
            verbose=False,
        )
    # Create LLM with development Azure OpenAI credentials
    else:
        # Get default Azure Deployment by service
        default_deployment = _get_default_deployment_by_service(service)
        if not default_deployment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot find default Azure Deployment by service '{service}'",
            )

        llm = AzureChatOpenAI(
            azure_deployment=default_deployment,
            temperature=0,
            verbose=False,
        )

    return llm
