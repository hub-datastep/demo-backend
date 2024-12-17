from fastapi import APIRouter
from fastapi_versioning import version

from infra.env import TGBOT_DELIVERY_NOTE_TOPIC
from infra.kafka import kafka_broker
from middleware.kafka_middleware import with_kafka_broker_connection

router = APIRouter()


@router.get("/test")
@version(1)
@with_kafka_broker_connection
async def send_message_to_kafka():
    message = "Hello World"

    await kafka_broker.publish(
        {"key": message},
        topic=TGBOT_DELIVERY_NOTE_TOPIC,

    )
    return message
