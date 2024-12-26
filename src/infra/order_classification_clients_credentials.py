from infra.env import (
    VYSOTA_AZURE_DEPLOYMENT_NAME_ORDER_CLASSIFICATION,
    VYSOTA_AZURE_OPENAI_API_KEY,
    VYSOTA_AZURE_OPENAI_ENDPOINT,
)
from scheme.order_classification.order_classification_config_scheme import OrderClassificationClient

ORDER_CLASSIFICATION_CLIENTS_CREDENTIALS = {
    f"{OrderClassificationClient.VYSOTA}": {
        "endpoint": VYSOTA_AZURE_OPENAI_ENDPOINT,
        "api_key": VYSOTA_AZURE_OPENAI_API_KEY,
        "deployment_name": VYSOTA_AZURE_DEPLOYMENT_NAME_ORDER_CLASSIFICATION,
    }
}
