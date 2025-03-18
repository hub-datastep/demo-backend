from sqlmodel import SQLModel

from scheme.order_classification.order_classification_scheme import MessageFileToSend


class MessageSendRequest(SQLModel):
    order_id: int
    message_text: str
    files: list[MessageFileToSend] | None = None
