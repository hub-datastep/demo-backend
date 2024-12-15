from faststream import FastStream

from infra.env import KAFKA_CONSUMER_GROUP, TGBOT_DELIVERY_NOTE_TOPIC
from infra.kafka import kafka_broker

app = FastStream(kafka_broker)

KAFKA_DEFAULT_BATCH_SETTINGS = {
    # Получать 1 сообщение (False) или несколько сразу (True)
    "batch": False,
    # Кол-во обрабатываемых сообщений за раз
    "max_records": 1,
    "auto_offset_reset": "earliest",
}


@kafka_broker.subscriber(
    TGBOT_DELIVERY_NOTE_TOPIC,
    group_id=KAFKA_CONSUMER_GROUP,
    **KAFKA_DEFAULT_BATCH_SETTINGS,
)
async def unistroy_parsing_with_mapping_consumer(body):
    # TODO: run parsing with mapping
    print(body)
