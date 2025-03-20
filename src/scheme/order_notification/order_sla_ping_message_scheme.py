from pydantic import BaseModel


class OrderSLAPingMessage(BaseModel):
    """
    Kafka Message for sending ping-message in telegram chat about SLA
    """

    message_text: str
    chat_id: str
