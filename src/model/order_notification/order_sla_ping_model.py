import asyncio

from fastapi import HTTPException, status
from loguru import logger

from infra.domyland.chats import get_message_template
from infra.domyland.constants import MessageTemplateName
from infra.domyland.orders import get_crm_order_url
from infra.env import env
from infra.kafka.brokers import kafka_broker
from infra.kafka.helpers import send_message_to_kafka
from middleware.kafka_middleware import with_kafka_broker_connection
from scheme.order_classification.order_classification_config_scheme import (
    MessageTemplate,
    ResponsibleUser,
)
from scheme.order_notification.order_sla_ping_message_scheme import OrderSLAPingMessage


@with_kafka_broker_connection(kafka_broker)
async def request_to_send_ping_message(
    order_id: int,
    message_text: str,
    chat_id: str,
):
    body = OrderSLAPingMessage(
        message_text=message_text,
        chat_id=chat_id,
    )
    await send_message_to_kafka(
        broker=kafka_broker,
        message_body=body,
        topic=env.KAFKA_ORDER_SLA_PING_MESSAGE_TOPIC,
        key=str(order_id),
    )


def start_order_sla_tracking(
    order_id: int,
    responsible_users_list: list[ResponsibleUser],
    messages_templates: list[MessageTemplate],
):
    # Get template for SLA ping-message
    template_name = MessageTemplateName.SLA_PING
    message_template = get_message_template(
        templates_list=messages_templates,
        template_name=template_name,
    )
    message_text = message_template.text

    # Combine CRM Order URL
    crm_order_url = get_crm_order_url(order_id=order_id)

    # TODO: Schedule pinging Responsible Users

    # Send ping-messages to Responsible Users
    for user in responsible_users_list:
        user_id = user.user_id
        telegram_username = user.telegram_username
        telegram_chat_id = user.telegram_chat_id

        # Check if Responsible User has Telegram username
        if not telegram_username:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Responsible user with ID '{user_id}' "
                    "has no telegram username, cannot send ping-message"
                ),
            )

        # Check if Responsible User has Telegram Chat ID
        if not telegram_chat_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Responsible user with ID '{user_id}' "
                    "has no telegram chat ID, cannot send ping-message"
                ),
            )

        # Format message
        formatted_message_text = message_text.format(
            telegram_username=telegram_username,
            crm_order_url=crm_order_url,
        )

        logger.debug(
            f"Ping-message for Responsible User:\n"
            f"ID: {user_id}\n"
            f"Telegram Username: {telegram_username}\n"
            f"Telegram Chat ID: {telegram_chat_id}"
        )
        logger.debug(f"Ping-message text:\n{formatted_message_text}")

        # Send request to ping Responsible User
        asyncio.run(
            request_to_send_ping_message(
                order_id=order_id,
                message_text=formatted_message_text,
                chat_id=telegram_chat_id,
            )
        )
