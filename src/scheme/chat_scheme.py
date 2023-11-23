from sqlmodel import SQLModel, Field, Relationship


class ChatBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")


class Chat(ChatBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    messages: list["Message"] = Relationship(
        sa_relationship_kwargs={"primaryjoin": "and_(Chat.id == Message.chat_id, Message.is_deleted == False)"}
    )
    user: "User" = Relationship(back_populates="chat")


class ChatCreate(ChatBase):
    pass


class ChatRead(ChatBase):
    id: int
    messages: list["MessageRead"]


from scheme.message_scheme import Message, MessageRead
from scheme.user_scheme import User

ChatRead.update_forward_refs()


