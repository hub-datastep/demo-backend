from fastapi import UploadFile
from pydantic import BaseModel


class QueryDto(BaseModel):
    chat_id: int | None = None
    query: str
    fileObject: UploadFile | None = None
    tables: list[str] | None
