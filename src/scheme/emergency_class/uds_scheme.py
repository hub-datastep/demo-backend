from sqlmodel import SQLModel


class UDS(SQLModel):
    user_id: str
    name: str
    address_list: list[str]
