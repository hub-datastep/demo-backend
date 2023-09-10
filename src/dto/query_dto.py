from fastapi import UploadFile
from pydantic import BaseModel


class QueryDto(BaseModel):
    chat_id: int = None
    query: str
    file: UploadFile = None
