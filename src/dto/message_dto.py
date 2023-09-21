from datetime import datetime

from pydantic import BaseModel

from dto.mark_dto import MarkOutDto
from dto.review_dto import ReviewOutDto


class MessageCreateDto(BaseModel):
    chat_id: int
    query: str | None = None
    answer: str | None = None
    sql: str | None = None
    table: str | None = None
    table_source: str | None = None
    exception: str | None = None
    connected_message_id: int | None = None
    is_deleted: bool | None = False


class MessageOutDto(MessageCreateDto):
    id: int
    created_at: datetime
    review: list[ReviewOutDto] | None = None
    mark: list[MarkOutDto] | None = None
