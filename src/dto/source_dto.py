from datetime import datetime

from pydantic import BaseModel


class SourceCreateDto(BaseModel):
    source_id: str
    chat_id: int
    file_name: str


class SourceDto(SourceCreateDto):
    id: int
    created_at: datetime
