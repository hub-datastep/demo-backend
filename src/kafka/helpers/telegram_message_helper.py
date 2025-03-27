from infra.env import env
from infra.kafka.brokers import kafka_broker
from infra.kafka.helpers import send_message_to_kafka
from middleware.kafka_middleware import with_kafka_broker_connection
from scheme.order_notification.order_telegram_message_scheme import OrderTelegramMessage


@with_kafka_broker_connection(kafka_broker)
async def request_to_send_telegram_message(
    order_id: int,
    message_text: str,
    chat_id: str,
    message_thread_id: int | None = None,
):
    body = OrderTelegramMessage(
        message_text=message_text,
        chat_id=chat_id,
        message_thread_id=message_thread_id,
    )
    await send_message_to_kafka(
        broker=kafka_broker,
        message_body=body,
        topic=env.KAFKA_ORDER_TELEGRAM_MESSAGE_TOPIC,
        key=str(order_id),
    )
