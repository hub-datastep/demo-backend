from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Env(BaseSettings):
    EXPERIMENTS_MODEL_NAME: str
    EXPERIMENTS_API_KEY: str
    EXPERIMENTS_AZURE_ENDPOINT: str


env = Env()
