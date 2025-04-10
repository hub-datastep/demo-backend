from dotenv import load_dotenv
from pydantic import BaseSettings

from infra.environment_type import EnvironmentType
from util.path_to_file_or_dir import find_path_to_file_or_dir

# _ENV_PATH = get_envfile_path()

# load_dotenv(dotenv_path=_ENV_PATH)
load_dotenv()


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
    AZURE_DEPLOYMENT_NAME_MAPPING: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    # Chroma Vector Store
    CHROMA_HOST: str
    CHROMA_PORT: int

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    @property
    def DB_CONNECTION_STRING(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DB_CONNECTION_STRING_ASYNC(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    DATA_FOLDER_PATH: str = find_path_to_file_or_dir("data")

    # Internal Kafka Settings
    # Broker & Auth
    KAFKA_SERVERS: str
    KAFKA_IS_USE_SSL: bool | None
    KAFKA_USERNAME: str
    KAFKA_PASSWORD: str
    # Consumers & Topics
    KAFKA_ORDERS_CONSUMERS_GROUP: str
    KAFKA_ORDER_NOTIFICATIONS_TOPIC: str
    KAFKA_ORDER_TELEGRAM_MESSAGE_TOPIC: str

    # Domyland Credentials
    # AI Account
    DOMYLAND_AUTH_AI_ACCOUNT_EMAIL: str
    DOMYLAND_AUTH_AI_ACCOUNT_PASSWORD: str
    DOMYLAND_AUTH_AI_ACCOUNT_TENANT_NAME: str
    # Public Account
    DOMYLAND_AUTH_PUBLIC_ACCOUNT_EMAIL: str
    DOMYLAND_AUTH_PUBLIC_ACCOUNT_PASSWORD: str
    DOMYLAND_AUTH_PUBLIC_ACCOUNT_TENANT_NAME: str

    # Vysota Azure OpenAI Credentials
    VYSOTA_AZURE_OPENAI_ENDPOINT: str
    VYSOTA_AZURE_OPENAI_API_KEY: str
    VYSOTA_AZURE_DEPLOYMENT_NAME_ORDER_CLASSIFICATION: str

    # Unistroy Azure OpenAI Credentials
    UNISTROY_AZURE_OPENAI_ENDPOINT: str
    UNISTROY_AZURE_OPENAI_API_KEY: str
    UNISTROY_AZURE_DEPLOYMENT_NAME_MAPPING: str

    # Unistroy Kafka
    UNISTROY_KAFKA_SERVERS: str
    UNISTROY_IS_KAFKA_WITH_SSL: bool
    UNISTROY_SASL_MECHANISM: str
    UNISTROY_SSL_CERT_FILE_PATH: str
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


env = Env()  # type: ignore
