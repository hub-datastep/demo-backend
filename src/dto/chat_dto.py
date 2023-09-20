from datetime import datetime

from pydantic import BaseModel

from dto.message_dto import MessageOutDto
from dto.source_dto import SourceOutDto


class ChatCreateDto(BaseModel):
    user_id: str


class ChatOutDto(ChatCreateDto):
    id: int
    created_at: datetime
    message: list[MessageOutDto] | None = None
    source: list[SourceOutDto]
