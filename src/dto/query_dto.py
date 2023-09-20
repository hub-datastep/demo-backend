from pydantic import BaseModel


class QueryDto(BaseModel):
    chat_id: int | None = None
    query: str
    source_id: str | None = None
