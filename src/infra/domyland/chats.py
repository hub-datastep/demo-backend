import requests
from fastapi import HTTPException, status

from infra.domyland.auth import (
    get_ai_account_auth_token,
    get_domyland_headers,
    get_public_account_auth_token,
)
from infra.domyland.constants import (
    DOMYLAND_API_BASE_URL,
    ORDER_CLIENT_CHAT_TARGET_TYPE_ID,
)
from infra.env import env
from infra.kafka.brokers import kafka_broker
from infra.kafka.helpers import send_message_to_kafka
from middleware.kafka_middleware import with_kafka_broker_connection
from scheme.kafka.send_message_consumer_scheme import MessageSendRequest
from scheme.order_classification.order_classification_config_scheme import (
    MessageTemplate,
)
from scheme.order_classification.order_classification_scheme import MessageFileToSend
from util.json_serializing import serialize_objs_list


def send_message_to_internal_chat(
    order_id: int,
    message: str,
) -> tuple[dict, dict]:
    """
    Send message to internal chat in order.
    Sender account - AI Account.
    """

    # Authorize in Domyland API
    auth_token = get_ai_account_auth_token()

    req_body = {
        "orderId": order_id,
        "text": message,
        "isImportant": False,
    }

    # Send message to internal chat
    response = requests.post(
        url=f"{DOMYLAND_API_BASE_URL}/order-comments",
        json=req_body,
        headers=get_domyland_headers(auth_token),
    )
    response_data = response.json()

    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Order internal chat POST: {response_data}",
        )

    return response_data, req_body


def send_message_to_resident_chat(
    order_id: int,
    text: str | None = None,
    files: list[MessageFileToSend] | None = None,
) -> tuple[dict, dict]:
    """
    Send message to chat with resident in order.
    Sender account - Public Account.
    """

    # Authorize in Domyland API
    auth_token = get_public_account_auth_token()

    req_params = {
        "targetId": order_id,
        "targetTypeId": ORDER_CLIENT_CHAT_TARGET_TYPE_ID,
    }
    req_body = {
        "text": text,
        "files": serialize_objs_list(files),
    }

    # Send message to internal chat
    response = requests.post(
        url=f"{DOMYLAND_API_BASE_URL}/chat",
        json=req_body,
        params=req_params,
        headers=get_domyland_headers(auth_token),
    )
    response_data = response.json()

    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Order client chat POST: {response_data}",
        )

    return response_data, req_body


def get_message_template(
    templates_list: list[MessageTemplate],
    template_name: str,
) -> MessageTemplate:
    """
    Get message template from list by name.
    """

    found_template: MessageTemplate | None = None
    for template in templates_list:
        if (
            template_name.strip()
            and template_name.lower().strip() in template.name.lower().strip()
            and not template.is_disabled
            and template.text
            and template.text.strip()
        ):
            found_template = template
            break

    # Check if template exists and enabled
    if not found_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Message template with name '{template_name}' "
                "not found or disabled or empty"
            ),
        )

    return found_template


@with_kafka_broker_connection(kafka_broker)
async def request_send_message_to_resident(
    order_id: int,
    message_text: str,
    files: list[MessageFileToSend] | None = None,
):
    body = MessageSendRequest(
        order_id=order_id,
        message_text=message_text,
        files=files,
    )
    await send_message_to_kafka(
        broker=kafka_broker,
        message_body=body,
        topic=env.KAFKA_ORDER_CHAT_MESSAGE_SENDING_TOPIC,
        key=str(order_id),
    )


if __name__ == "__main__":
    # Test Order ID with chat
    order_id = 3301805

    # Message Text
    text = "Test message"

    # List of files names from Domyland
    files_names = [
        "659b2959e8ec468cacb11611b7651c7f.jpg",
    ]

    send_message_to_resident_chat(
        order_id=order_id,
        text=text,
        files=[MessageFileToSend(fileName=name) for name in files_names],
    )
