import asyncio

from faststream import FastStream
from loguru import logger

from infra.domyland.chats import send_message_to_resident_chat
from infra.env import env
from infra.kafka.brokers import kafka_broker
from scheme.kafka.send_message_consumer_scheme import MessageSendRequest

app = FastStream(
    kafka_broker,
    title="Order Chat Message Sending",
)

_KAFKA_SETTINGS = {
    "group_id": env.KAFKA_ORDERS_CONSUMERS_GROUP,
    # Получать 1 сообщение (False) или несколько сразу (True)
    "batch": False,
    # Кол-во обрабатываемых сообщений за раз
    "max_records": 1,
    # Если нет смещения, читать только последнее сообщение
    "auto_offset_reset": "latest",
}


@kafka_broker.subscriber(
    env.KAFKA_ORDER_CHAT_MESSAGE_SENDING_TOPIC,
    **_KAFKA_SETTINGS,
)
async def order_chat_message_send_consumer(
    body: MessageSendRequest,
):
    logger.debug(
        f"Message text for Order with ID {body.order_id}:\n{body.message_text}"
    )

    send_message_to_resident_chat(
        order_id=body.order_id,
        text=body.message_text,
    )


if __name__ == "__main__":
    asyncio.run(app.run())
