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
    "batch": True,
    # Кол-во обрабатываемых сообщений за раз
    "max_records": 100,
    # Если нет смещения, читать только последнее сообщение
    "auto_offset_reset": "latest",
}


@kafka_broker.subscriber(
    env.KAFKA_ORDER_CHAT_MESSAGE_SENDING_TOPIC,
    **_KAFKA_SETTINGS,
)
async def order_chat_message_send_consumer(
    messages_list: list[MessageSendRequest],
):
    logger.debug(f"Messages batch ({len(messages_list)} items):\n{messages_list}")

    # If no messages, just exit
    if not messages_list:
        return

    # Collecting unique messages list to send resident
    messages_to_send: dict[str, MessageSendRequest] = {}
    for message in messages_list:
        order_id = message.order_id
        if str(order_id) not in list(messages_to_send.keys()):
            messages_to_send.update({f"{order_id}": message})

    # Send messages to residents orders chats
    for _, message in messages_to_send.items():
        order_id = message.order_id
        message_text = message.message_text
        files = message.files

        logger.debug(f"Message for Order with ID {order_id}")
        logger.debug(f"Message text:\n{message_text}")
        logger.debug(f"Files:\n{files}")

        send_message_to_resident_chat(
            order_id=order_id,
            text=message.message_text,
            files=files,
        )


if __name__ == "__main__":
    asyncio.run(app.run())
