from fastapi import APIRouter, Depends
from fastapi_versioning import version

from infra.env import TGBOT_DELIVERY_NOTE_TOPIC
from infra.kafka import kafka_broker
from middleware.kafka_middleware import with_kafka_broker_connection
from model.auth.auth_model import get_current_user
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("/test")
@version(1)
@with_kafka_broker_connection
async def send_test_message_to_kafka(
    current_user: UserRead = Depends(get_current_user),
):
    message = "Hello World"

    await kafka_broker.publish(
        {"key": message},
        topic=TGBOT_DELIVERY_NOTE_TOPIC,

    )
    return message
