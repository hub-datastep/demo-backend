from datetime import datetime

from pydantic import BaseModel


class ReviewCreateDto(BaseModel):
    commentary: str | None = None
    mark: int | None = None
    message_id: int


class ReviewOutDto(ReviewCreateDto):
    created_at: datetime
