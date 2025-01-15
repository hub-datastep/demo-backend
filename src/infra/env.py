import os
from distutils.util import strtobool

from dotenv import load_dotenv

load_dotenv()


class Environment:
    DEV = "development"
    PROD = "production"


ENVIRONMENT = os.getenv("ENVIRONMENT")
IS_DEV_ENV = ENVIRONMENT == Environment.DEV

FRONTEND_URL = os.getenv("FRONTEND_URL")

NER_SERVICE_URL = os.getenv("NER_SERVICE_URL")

AZURE_DEPLOYMENT_NAME_DB_ASSISTANT = os.getenv("AZURE_DEPLOYMENT_NAME_DB_ASSISTANT")
AZURE_DEPLOYMENT_NAME_SIMILAR_QUERIES = os.getenv(
    "AZURE_DEPLOYMENT_NAME_SIMILAR_QUERIES"
)
AZURE_DEPLOYMENT_NAME_DOCS_ASSISTANT = os.getenv("AZURE_DEPLOYMENT_NAME_DOCS_ASSISTANT")
AZURE_DEPLOYMENT_NAME_EMBEDDINGS = os.getenv("AZURE_DEPLOYMENT_NAME_EMBEDDINGS")
AZURE_DEPLOYMENT_CIM_MAPPING = os.getenv("AZURE_DEPLOYMENT_CIM_MAPPING")
AZURE_DEPLOYMENT_NAME_NOMENCLATURE_VIEW = os.getenv('AZURE_DEPLOYMENT_NAME_NOMENCLATURE_VIEW')
AZURE_DEPLOYMENT_NAME_ORDER_CLASSIFICATION = os.getenv(
    "AZURE_DEPLOYMENT_NAME_ORDER_CLASSIFICATION"
)

# Redis
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Chroma Vector Store
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = os.getenv("CHROMA_PORT")

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")

DATA_FOLDER_PATH = os.getenv("DATA_FOLDER_PATH")

# Domyland Credentials
DOMYLAND_AUTH_EMAIL = os.getenv("DOMYLAND_AUTH_EMAIL")
DOMYLAND_AUTH_PASSWORD = os.getenv("DOMYLAND_AUTH_PASSWORD")
DOMYLAND_AUTH_TENANT_NAME = os.getenv("DOMYLAND_AUTH_TENANT_NAME")

# Vysota Azure OpenAI Credentials
VYSOTA_AZURE_OPENAI_ENDPOINT = os.getenv("VYSOTA_AZURE_OPENAI_ENDPOINT")
VYSOTA_AZURE_OPENAI_API_KEY = os.getenv("VYSOTA_AZURE_OPENAI_API_KEY")
VYSOTA_AZURE_DEPLOYMENT_NAME_ORDER_CLASSIFICATION = os.getenv(
    "VYSOTA_AZURE_DEPLOYMENT_NAME_ORDER_CLASSIFICATION"
)

# Unistroy Kafka
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_USERNAME = os.getenv("KAFKA_USERNAME")
KAFKA_PASSWORD = os.getenv("KAFKA_PASSWORD")
SASL_MECHANISM = os.getenv("SASL_MECHANISM")
KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP")
TGBOT_DELIVERY_NOTE_TOPIC = os.getenv("TGBOT_DELIVERY_NOTE_TOPIC")
TGBOT_DELIVERY_NOTE_EXPORT_TOPIC = os.getenv("TGBOT_DELIVERY_NOTE_EXPORT_TOPIC")
IS_KAFKA_WITH_SSL = strtobool(os.getenv("IS_KAFKA_WITH_SSL", "False"))
# NSI
KAFKA_NSI_CONSUMERS_GROUP = os.getenv("KAFKA_NSI_CONSUMERS_GROUP")
KAFKA_NSI_TOPIC_CATEGORIES = os.getenv("KAFKA_NSI_TOPIC_CATEGORIES")
KAFKA_NSI_TOPIC_MATERIALS = os.getenv("KAFKA_NSI_TOPIC_MATERIALS")
