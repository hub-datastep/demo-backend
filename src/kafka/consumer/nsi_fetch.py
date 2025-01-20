import json
import os
from datetime import datetime
from pathlib import Path

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

KAFKA_NSI_TOPICS_SETTINGS = {
    "batch": True,
    "max_records": 1_000_000,
    "auto_offset_reset": "earliest",
}


def _get_path_for_files():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    uuid = generate_uuid()
    messages_path = f"{DATA_FOLDER_PATH}/unistroy/kafka-nsi/{now}"

    return messages_path, uuid


def _save_to_json(file_path: str, data):
    # Create parent dirs if not exists
    os.makedirs(Path(file_path).parent, exist_ok=True)

    with open(file_path, 'w') as f:
        json.dump(data, f, ensure_ascii=False)


@kafka_broker.subscriber(
    KAFKA_NSI_TOPIC_CATEGORIES,
    group_id=KAFKA_NSI_CONSUMERS_GROUP,
    **KAFKA_NSI_TOPICS_SETTINGS,
)
async def get_all_categories(body):
    """
    Консьюмер для выгрузки всех категорий для материалов из НСИ
    """
    files_path, uuid = _get_path_for_files()
    categories_path = f"{files_path}/categories/{uuid}.json"
    _save_to_json(categories_path, body)


@kafka_broker.subscriber(
    KAFKA_NSI_TOPIC_MATERIALS,
    group_id=KAFKA_NSI_CONSUMERS_GROUP,
    **KAFKA_NSI_TOPICS_SETTINGS,
)
async def get_all_materials(body):
    """
    Консьюмер для выгрузки всех материалов из НСИ
    """
    files_path, uuid = _get_path_for_files()
    materials_path = f"{files_path}/materials/{uuid}.json"
    _save_to_json(materials_path, body)
