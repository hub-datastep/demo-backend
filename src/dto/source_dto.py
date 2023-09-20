from datetime import datetime

from pydantic import BaseModel


class SourceCreateDto(BaseModel):
    source_id: str
    file_name: str
    chat_id: int


class SourceOutDto(BaseModel):
    id: int
    source_id: str
    file_name: str
    chat_id: int
    created_at: datetime
