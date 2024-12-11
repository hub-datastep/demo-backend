from fastapi import APIRouter, Depends
from fastapi_versioning import version
from infra.kafka import broker, with_broker_connection
from infra.env import TGBOT_DELIVERY_NOTE_TOPIC

router = APIRouter()


@router.get("")
@version(1)
@with_broker_connection
async def index():
    try:
        await broker.publish({"key": 'hello world'}, topic=TGBOT_DELIVERY_NOTE_TOPIC)
    except Exception as e:
        print(f"Ошибка при публикации сообщения: {e}")
    return 'Hello world!'
