from faststream import FastStream
from loguru import logger

from infra.env import (
    KAFKA_CONSUMER_GROUP,
    TGBOT_DELIVERY_NOTE_TOPIC,
    TGBOT_DELIVERY_NOTE_EXPORT_TOPIC, DATA_FOLDER_PATH,
)
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
# @kafka_broker.subscriber(
#     TGBOT_DELIVERY_NOTE_TOPIC,
#     group_id=KAFKA_CONSUMER_GROUP,
#     **KAFKA_DEFAULT_BATCH_SETTINGS,
# )
# async def unistroy_mapping_with_parsing_consumer(body: UTDCardInputMessage):
#     logger.debug(f"Unistroy Kafka Request (input message):\n{body}")
#
#     # Run mapping with parsing and wait results
#     output_messages_list = mapping_with_parsing_model.parse_and_map_utd_card(body=body)
#
#     async for output_message in output_messages_list:
#         logger.debug(f"Unistroy Kafka Response (output message):\n{output_message}")
#
#         # Send message to Unistroy Kafka export-topic with results
#         await send_message_to_kafka(
#             message_body=output_message.dict(),
#             topic=TGBOT_DELIVERY_NOTE_EXPORT_TOPIC,
#         )


# ! У нас нет пока нет прав на чтение этого топика, только на запись
# @kafka_broker.subscriber(
#     TGBOT_DELIVERY_NOTE_EXPORT_TOPIC,
#     group_id=KAFKA_CONSUMER_GROUP,
#     **KAFKA_DEFAULT_BATCH_SETTINGS,
# )
# async def mapping_results_consumer(body):
#     logger.debug(f"Unistroy mapping results: {body}")


@kafka_broker.subscriber(
    "1cbsh.material-category.out.1",
    group_id=KAFKA_CONSUMER_GROUP,
    **{
        "batch": True,
        "max_records": 1_000_000,
        "auto_offset_reset": "earliest",
    },
)
async def get_all_messages(body):
    messages_path = f"{DATA_FOLDER_PATH}/kafka_messages.txt"
    with open(messages_path, 'w') as f:
        f.write(str(body))
