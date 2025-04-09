from infra.env import env
from infra.kafka.brokers import kafka_broker
from infra.kafka.helpers import send_message_to_kafka
from scheme.order_notification.order_telegram_message_scheme import OrderTelegramMessage


async def request_to_send_telegram_message(
    message_key: str,
    message_text: str,
    chat_id: str,
    message_thread_id: int | None = None,
) -> OrderTelegramMessage:
    """
    Sends Telegram message by publishing it to Kafka topic.

    Args:
        message_key (str): Unique key for Kafka message.
        message_text (str): Text content of Telegram message.
        chat_id (str): Telegram chat ID where the message will be sent.
        message_thread_id (int | None): ID of the Telegram thread.

    Returns:
        OrderTelegramMessage: Kafka message that was sent.
    """

    message_body = OrderTelegramMessage(
        message_text=message_text,
        chat_id=chat_id,
        message_thread_id=message_thread_id,
    )
    await send_message_to_kafka(
        broker=kafka_broker,
        message_body=message_body,
        topic=env.KAFKA_ORDER_TELEGRAM_MESSAGE_TOPIC,
        key=message_key,
    )
    return message_body
