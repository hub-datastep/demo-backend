from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship

from scheme.chat.message_scheme import Message


class ReviewBase(SQLModel):
    commentary: str


class Review(ReviewBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    message_id: int = Field(foreign_key="message.id")
    message: Message = Relationship(back_populates="reviews")
    created_at: datetime | None = Field(default=datetime.utcnow())


class ReviewCreate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    id: int
