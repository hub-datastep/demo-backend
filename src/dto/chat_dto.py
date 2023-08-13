from datetime import datetime

from pydantic import BaseModel

from dto.message_dto import MessageOutDto


class ChatCreateDto(BaseModel):
    user_id: str


class ChatOutDto(ChatCreateDto):
    id: int
    created_at: datetime
    message: list[MessageOutDto] | None = None
