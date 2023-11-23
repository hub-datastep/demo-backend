from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship

from scheme.message_scheme import Message


class MarkBase(SQLModel):
    mark: bool


class Mark(MarkBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    message_id: int = Field(foreign_key="message.id")
    message: Message = Relationship(back_populates="mark")
    created_at: datetime | None = Field(default=datetime.utcnow())


class MarkCreate(MarkBase):
    message_id: int


class MarkRead(MarkBase):
    id: int
