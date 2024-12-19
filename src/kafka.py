from faststream import FastStream
from loguru import logger

from infra.env import KAFKA_CONSUMER_GROUP, TGBOT_DELIVERY_NOTE_TOPIC, TGBOT_DELIVERY_NOTE_EXPORT_TOPIC
from infra.kafka import kafka_broker, send_message_to_kafka
from model.mapping import mapping_with_parsing_model
from scheme.file.utd_card_message_scheme import UTDCardInputMessage

app = FastStream(kafka_broker)

KAFKA_DEFAULT_BATCH_SETTINGS = {
    # Получать 1 сообщение (False) или несколько сразу (True)
    "batch": False,
    # Кол-во обрабатываемых сообщений за раз
    "max_records": 1,
    "auto_offset_reset": "earliest",
}


# Unistroy UTD PDF files Mapping Subscriber
# Gets messages from topic
@kafka_broker.subscriber(
    TGBOT_DELIVERY_NOTE_TOPIC,
    group_id=KAFKA_CONSUMER_GROUP,
    **KAFKA_DEFAULT_BATCH_SETTINGS,
)
async def unistroy_mapping_with_parsing_consumer(body: UTDCardInputMessage):
    logger.debug(f"Unistroy Kafka Request (input message):\n{body}")

    # Run mapping with parsing and wait results
    output_message = mapping_with_parsing_model.parse_and_map_utd_card(body=body)

    # Send message to Unistroy Kafka export-topic with results
    logger.debug(f"Unistroy Kafka Response (output message):\n{output_message}")
    await send_message_to_kafka(
        message_body=output_message.dict(),
        topic=TGBOT_DELIVERY_NOTE_EXPORT_TOPIC,
    )

# ! У нас нет пока нет прав на чтение этого топика, только на запись
# @kafka_broker.subscriber(
#     TGBOT_DELIVERY_NOTE_EXPORT_TOPIC,
#     group_id=KAFKA_CONSUMER_GROUP,
#     **KAFKA_DEFAULT_BATCH_SETTINGS,
# )
# async def mapping_results_consumer(body):
#     logger.debug(f"Unistroy mapping results: {body}")
