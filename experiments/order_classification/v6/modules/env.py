from pydantic import BaseSettings


class Env(BaseSettings):
    MODEL_NAME: str
    API_KEY: str
    AZURE_ENDPOINT: str


env = Env()
