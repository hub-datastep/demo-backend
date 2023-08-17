from pydantic import BaseModel


class QueryDto(BaseModel):
    query: str
