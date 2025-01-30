from infra.env import env
from scheme.order_classification.order_classification_config_scheme import OrderClassificationClient

ORDER_CLASSIFICATION_CLIENTS_CREDENTIALS = {
    f"{OrderClassificationClient.VYSOTA}": {
        "endpoint": env.VYSOTA_AZURE_OPENAI_ENDPOINT,
        "api_key": env.VYSOTA_AZURE_OPENAI_API_KEY,
        "deployment_name": env.VYSOTA_AZURE_DEPLOYMENT_NAME_ORDER_CLASSIFICATION,
    }
}
