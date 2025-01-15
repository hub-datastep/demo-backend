import json
import os
from datetime import datetime

from faststream import FastStream

from infra.env import (
    DATA_FOLDER_PATH,
    KAFKA_NSI_TOPIC_MATERIALS,
    KAFKA_NSI_TOPIC_CATEGORIES,
    KAFKA_NSI_CONSUMERS_GROUP,
)
from infra.kafka import kafka_broker
from util.uuid import generate_uuid

app = FastStream(kafka_broker)

KAFKA_DEFAULT_SETTINGS = {
    # Получать 1 сообщение (False) или несколько сразу (True)
    "batch": False,
    # Кол-во обрабатываемых сообщений за раз
    "max_records": 1,
    "auto_offset_reset": "earliest",
}

KAFKA_NSI_TOPICS_SETTINGS = {
    "batch": True,
    "max_records": 1_000_000,
    "auto_offset_reset": "earliest",
}


def _get_path_for_files():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    uuid = generate_uuid()
    messages_path = f"{DATA_FOLDER_PATH}/unistroy/kafka-nsi/{now}/{uuid}"

    # Create all parent folder if not exists
    os.makedirs(messages_path, exist_ok=True)

    return messages_path


# Unistroy UTD PDF files Mapping Subscriber
# Gets messages from topic
# @kafka_broker.subscriber(
#     TGBOT_DELIVERY_NOTE_TOPIC,
#     group_id=KAFKA_CONSUMER_GROUP,
#     **KAFKA_DEFAULT_SETTINGS,
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


# * Выгрузка категорий из топика
@kafka_broker.subscriber(
    KAFKA_NSI_TOPIC_CATEGORIES,
    group_id=KAFKA_NSI_CONSUMERS_GROUP,
    **KAFKA_NSI_TOPICS_SETTINGS,
)
async def get_all_messages(body):
    """
    Консьюмер для выгрузки всех категорий для материалов из НСИ
    """
    files_path = _get_path_for_files()
    messages_path = f"{files_path}/kafka_messages-categories.json"
    with open(messages_path, 'w') as f:
        json.dump(body, f, ensure_ascii=False)


# * Выгрузка материалов из топика
@kafka_broker.subscriber(
    KAFKA_NSI_TOPIC_MATERIALS,
    group_id=KAFKA_NSI_CONSUMERS_GROUP,
    **KAFKA_NSI_TOPICS_SETTINGS,
)
async def get_all_messages(body):
    """
    Консьюмер для выгрузки всех материалов из НСИ
    """
    files_path = _get_path_for_files()
    messages_path = f"{files_path}/kafka_messages-materials.json"
    with open(messages_path, 'w') as f:
        json.dump(body, f, ensure_ascii=False)
