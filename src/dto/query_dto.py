from pydantic import BaseModel


class QueryDto(BaseModel):
    chat_id: int | None = None
    query: str
    filename: str | None = None
    tables: list[str] | None = None
