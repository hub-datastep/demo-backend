from fastapi import APIRouter, Depends
from fastapi_versioning import version

from infra.env import TGBOT_DELIVERY_NOTE_TOPIC
from infra.kafka import send_message_to_kafka
from middleware.kafka_middleware import with_kafka_broker_connection
from model.auth.auth_model import get_current_user
from scheme.file.utd_card_message_scheme import UTDCardInputMessage
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.post("/test")
@version(1)
@with_kafka_broker_connection
async def send_test_message_to_kafka(
    current_user: UserRead = Depends(get_current_user),
):
    message = "Hello World"
    await send_message_to_kafka(
        message_body={"key": message},
        topic=TGBOT_DELIVERY_NOTE_TOPIC,
    )
    return message


@router.post("/utd_card")
@version(1)
@with_kafka_broker_connection
async def send_utd_card_message_to_kafka(
    body: UTDCardInputMessage,
    current_user: UserRead = Depends(get_current_user),
):
    await send_message_to_kafka(
        message_body=body,
        topic=TGBOT_DELIVERY_NOTE_TOPIC,
    )
    return "Message sent"
