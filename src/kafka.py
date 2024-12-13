from faststream import FastStream

from infra.kafka import broker

import infra.env as settings

app = FastStream(broker)

KAFKA_DEFAULT_BATCH_SETTINGS = {
    "batch": False,  # NOTE: Получать 1 сообщение (False) или несколько сразу (True)
    "max_records": 1,  # NOTE: кол-во обрабатываемых сообщений за раз
    "auto_offset_reset": "earliest",
}


@broker.subscriber(
    settings.TGBOT_DELIVERY_NOTE_TOPIC,
    group_id=settings.KAFKA_CONSUMER_GROUP,
    **KAFKA_DEFAULT_BATCH_SETTINGS,
)
async def example_consumer(body):
    print(body)
