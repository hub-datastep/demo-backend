from datetime import datetime

from pydantic import BaseModel


class MarkCreateDto(BaseModel):
    message_id: int
    mark: int
    created_by: int


class MarkOutDto(MarkCreateDto):
    id: int
    created_at: datetime