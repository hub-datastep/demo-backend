from sqlmodel import SQLModel


class MessageSendRequest(SQLModel):
    order_id: int
    message_text: str
