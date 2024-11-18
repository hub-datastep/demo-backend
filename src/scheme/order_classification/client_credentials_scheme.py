from sqlmodel import SQLModel


class ClientCredentials(SQLModel):
    endpoint: str
    api_key: str
    deployment_name: str
