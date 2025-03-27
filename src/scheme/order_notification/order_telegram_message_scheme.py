from sqlmodel import SQLModel


class OrderTelegramMessage(SQLModel):
    """
    Kafka Message for sending message in Telegram Chat
    """

    message_text: str
    chat_id: str
    message_thread_id: int | None = None
