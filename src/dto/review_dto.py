from datetime import datetime

from pydantic import BaseModel


class ReviewCreateDto(BaseModel):
    commentary: str | None = None
    message_id: int
    created_by: int


class ReviewOutDto(ReviewCreateDto):
    id: int
    created_at: datetime
