from dotenv import load_dotenv
from pydantic import BaseSettings

from infra.environment_type import EnvironmentType
from util.env_files import get_envfile_path
from util.path_to_file_or_dir import find_path_to_file_or_dir

_ENV_PATH = get_envfile_path()

load_dotenv(dotenv_path=_ENV_PATH)


class Env(BaseSettings):
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEV

    # noinspection PyPep8Naming
    @property
    def IS_DEV_ENV(self) -> bool:
        return self.ENVIRONMENT == EnvironmentType.DEV

    FRONTEND_URL: str
    NER_SERVICE_URL: str

    # Azure Deployments
    AZURE_DEPLOYMENT_NAME_DB_ASSISTANT: str
    AZURE_DEPLOYMENT_NAME_SIMILAR_QUERIES: str
    AZURE_DEPLOYMENT_NAME_DOCS_ASSISTANT: str
    AZURE_DEPLOYMENT_NAME_EMBEDDINGS: str
    AZURE_DEPLOYMENT_CIM_MAPPING: str | None
    AZURE_DEPLOYMENT_NAME_NOMENCLATURE_VIEW: str
    AZURE_DEPLOYMENT_NAME_ORDER_CLASSIFICATION: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    # Chroma Vector Store
    CHROMA_HOST: str
    CHROMA_PORT: int

    # DB
    DB_CONNECTION_STRING: str

    DATA_FOLDER_PATH: str = find_path_to_file_or_dir("data")

    # Domyland Credentials
    DOMYLAND_AUTH_EMAIL: str
    DOMYLAND_AUTH_PASSWORD: str
    DOMYLAND_AUTH_TENANT_NAME: str

    # Vysota Azure OpenAI Credentials
    VYSOTA_AZURE_OPENAI_ENDPOINT: str
    VYSOTA_AZURE_OPENAI_API_KEY: str
    VYSOTA_AZURE_DEPLOYMENT_NAME_ORDER_CLASSIFICATION: str

    # Unistroy Kafka
    UNISTROY_KAFKA_SERVERS: str
    UNISTROY_IS_KAFKA_WITH_SSL: bool
    UNISTROY_SASL_MECHANISM: str
    # Credentials
    UNISTROY_KAFKA_USERNAME: str
    UNISTROY_KAFKA_PASSWORD: str
    # Mapping Consumers & Topics
    UNISTROY_KAFKA_CONSUMERS_GROUP: str
    UNISTROY_MAPPING_INPUT_TOPIC: str
    UNISTROY_MAPPING_LINK_OUTPUT_TOPIC: str
    UNISTROY_MAPPING_RESULTS_OUTPUT_TOPIC: str
    # NSI Consumers & Topics
    UNISTROY_KAFKA_NSI_CONSUMERS_GROUP: str
    UNISTROY_KAFKA_NSI_CATEGORIES_TOPIC: str
    UNISTROY_KAFKA_NSI_MATERIALS_TOPIC: str


env = Env()
