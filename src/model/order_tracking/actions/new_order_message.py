import asyncio

from loguru import logger

from infra.domyland.chats import get_message_template
from infra.domyland.constants import MessageTemplateName
from infra.domyland.orders import get_crm_order_url
from kafka.helpers.telegram_message_helper import request_to_send_telegram_message
from model.order_tracking.helpers.telegram_chat import get_responsible_user_telegram
from scheme.order_classification.order_classification_config_scheme import (
    MessageTemplate,
    ResponsibleUser,
)


def send_new_order_message(
    order_id: int,
    order_address: str,
    responsible_user: ResponsibleUser,
    messages_templates: list[MessageTemplate],
):
    """
    Send New Order Message to Responsible User in Telegram Chat.
    """

    user_id = responsible_user.user_id

    # * Get template for SLA ping-message
    template_name = MessageTemplateName.NEW_ORDER
    message_template = get_message_template(
        templates_list=messages_templates,
        template_name=template_name,
    )
    message_text = message_template.text

    # * Combine CRM Order URL
    crm_order_url = get_crm_order_url(order_id=order_id)

    # * Get Telegram of Responsible User
    telegram_username, telegram_chat_id, telegram_thread_id = (
        get_responsible_user_telegram(
            order_address=order_address,
            responsible_user=responsible_user,
        )
    )

    # * Format message
    formatted_message_text = message_text.format(
        telegram_username=telegram_username,
        crm_order_url=crm_order_url,
    )

    logger.debug(
        f"New Order Message for Responsible User:\n"
        f"ID: {user_id}\n"
        f"Telegram Username: {telegram_username}\n"
        f"Telegram Chat ID: {telegram_chat_id}\n"
        f"Telegram Topic ID: {telegram_thread_id}\n"
        f"Message text:\n{formatted_message_text}"
    )

    # * Request Telegram message for Responsible User
    logger.success(f"Sending New Order Message...")
    asyncio.run(
        request_to_send_telegram_message(
            order_id=order_id,
            message_text=formatted_message_text,
            chat_id=telegram_chat_id,
            message_thread_id=telegram_thread_id,
        )
    )
