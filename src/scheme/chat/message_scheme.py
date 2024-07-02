from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Relationship, Field


class MessageBase(SQLModel):
    query: str = ""
    answer: str = ""
    sql: str = ""
    table: str = ""
    table_source: str = ""
    is_deleted: bool = Field(default=False)
    connected_message_id: int | None = Field(default=None, foreign_key="message.id")
    chat_id: int = Field(foreign_key="chat.id")


class Message(MessageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    chat: "Chat" = Relationship(back_populates="messages")
    reviews: list["Review"] = Relationship(back_populates="message")
    mark: "Mark" = Relationship(back_populates="message")
    created_at: datetime | None = Field(default=datetime.utcnow())


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: int
    reviews: list["Review"]
    mark: Optional["Mark"]


from scheme.chat.chat_scheme import Chat
from scheme.chat.mark_scheme import Mark
from scheme.chat.review_scheme import Review

Message.update_forward_refs()
MessageRead.update_forward_refs()
