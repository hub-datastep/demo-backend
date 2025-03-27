from sqlmodel import SQLModel


class OrderTelegramMessage(SQLModel):
    """
    Kafka Message for sending message in Telegram Chat about SLA
    """

    message_text: str
    chat_id: str
