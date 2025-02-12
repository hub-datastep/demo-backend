from pydantic import BaseSettings


class Env(BaseSettings):
    OPENAI_API_KEY_ORDER_CLASSIFICATION_EVALUATION: str


env = Env()
