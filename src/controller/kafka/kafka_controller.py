from fastapi import APIRouter, Depends
from fastapi_versioning import version

from infra.env import env
from infra.kafka.brokers import kafka_broker, unistroy_kafka_broker
from infra.kafka.helpers import send_message_to_kafka
from middleware.kafka_middleware import with_kafka_broker_connection
from model.auth.auth_model import get_current_user
from scheme.file.utd_card_message_scheme import UTDCardInputMessage
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.post("/test")
@version(1)
@with_kafka_broker_connection(kafka_broker)
async def send_test_message_to_kafka(
    topic: str,
    current_user: UserRead = Depends(get_current_user),
):
    message = "Hello from Datastep!!"
    await send_message_to_kafka(
        broker=kafka_broker,
        message_body=message,
        topic=topic,
    )
    return message


@router.post("/utd_card")
@version(1)
@with_kafka_broker_connection(unistroy_kafka_broker)
async def send_utd_card_message_to_kafka(
    body: UTDCardInputMessage,
    current_user: UserRead = Depends(get_current_user),
):
    await send_message_to_kafka(
        broker=unistroy_kafka_broker,
        message_body=body,
        topic=env.UNISTROY_MAPPING_INPUT_TOPIC,
    )
    return body.dict()
