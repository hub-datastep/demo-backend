from fastapi import APIRouter
from fastapi_versioning import version

from infra.env import TGBOT_DELIVERY_NOTE_TOPIC
from infra.kafka import kafka_broker
from middleware.kafka_middleware import with_kafka_broker_connection

router = APIRouter()


@router.get("")
@version(1)
@with_kafka_broker_connection
async def index():
    try:
        await kafka_broker.publish(
            {"key": 'hello world'},
            topic=TGBOT_DELIVERY_NOTE_TOPIC,
        )
    except Exception as e:
        print(f"Ошибка при публикации сообщения: {e}")
    return 'Hello world!'
