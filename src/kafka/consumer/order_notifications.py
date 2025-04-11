import asyncio

from faststream import FastStream

from infra.env import env
from infra.kafka.brokers import kafka_broker
from model.order_notification import order_notification_model
from scheme.order_notification.order_notification_scheme import (
    OrderNotificationRequestBody,
)

app = FastStream(
    kafka_broker,
    title="Order Notifications",
)

_SETTINGS = {
    "group_id": env.KAFKA_ORDERS_CONSUMERS_GROUP,
    # Получать 1 сообщение (False) или несколько сразу (True)
    "batch": True,
    # Кол-во обрабатываемых сообщений за раз
    "max_records": 100,
    # Если нет смещения, читать только последнее сообщение
    "auto_offset_reset": "latest",
}

WAIT_TIME_IN_SEC = 30


@kafka_broker.subscriber(
    env.KAFKA_ORDER_NOTIFICATIONS_TOPIC,
    **_SETTINGS,
)
async def process_order_status_updated_event(
    messages_list: list[OrderNotificationRequestBody],
):
    for message in messages_list:
        await order_notification_model.process_event(
            body=message,
            client=message.client,
        )


if __name__ == "__main__":
    asyncio.run(app.run())
