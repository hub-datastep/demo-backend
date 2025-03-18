from sqlmodel import SQLModel


class KafkaBrokerSettings(SQLModel):
    servers_list: list[str]
    username: str
    password: str
    is_use_ssl: bool | None = None
    ssl_cert_file_path: str | None = None
