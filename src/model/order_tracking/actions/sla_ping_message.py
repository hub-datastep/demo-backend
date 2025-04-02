import asyncio

from fastapi import HTTPException, status
from loguru import logger

from infra.domyland.chats import get_message_template
from infra.domyland.constants import MessageTemplateName
from infra.domyland.orders import get_crm_order_url
from kafka.helpers.telegram_message_helper import request_to_send_telegram_message
from scheme.order_classification.order_classification_config_scheme import (
    MessageTemplate,
    ResponsibleUser,
)
from util.seconds_to_time_str import get_time_str_from_seconds


def send_sla_ping_message(
    order_id: int,
    responsible_user: ResponsibleUser,
    messages_templates: list[MessageTemplate],
    sla_solve_time_in_sec: int,
):
    # * Get template for SLA ping-message
    template_name = MessageTemplateName.SLA_PING
    message_template = get_message_template(
        templates_list=messages_templates,
        template_name=template_name,
    )
    message_text = message_template.text

    # * Combine CRM Order URL
    crm_order_url = get_crm_order_url(order_id=order_id)

    user_id = responsible_user.user_id
    telegram_username = responsible_user.telegram_username
    telegram_chat_id = responsible_user.telegram_chat_id
    telegram_thread_id = responsible_user.telegram_thread_id

    # * Check if Responsible User has Telegram username
    if not telegram_username:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Responsible user with ID '{user_id}' "
                "has no telegram username, cannot send ping-message"
            ),
        )

    # * Check if Responsible User has Telegram Chat ID
    if not telegram_chat_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Responsible user with ID '{user_id}' "
                "has no telegram chat ID, cannot send ping-message"
            ),
        )

    # * Get SLA time text
    sla_time_str = get_time_str_from_seconds(seconds=abs(sla_solve_time_in_sec))
    if sla_solve_time_in_sec > 0:
        sla_time_text = (
            f"До окончания SLA времени выполнения этой заявки осталось {sla_time_str}"
        )
    else:
        sla_time_text = (
            f"SLA времени выполнения этой заявки просрочен на {sla_time_str}"
        )

    # * Format message
    formatted_message_text = message_text.format(
        telegram_username=telegram_username,
        sla_time_text=sla_time_text,
        crm_order_url=crm_order_url,
    )

    logger.debug(
        f"Ping-message for Responsible User:\n"
        f"ID: {user_id}\n"
        f"Telegram Username: {telegram_username}\n"
        f"Telegram Chat ID: {telegram_chat_id}"
    )
    logger.debug(f"Ping-message text:\n{formatted_message_text}")

    # * Request Telegram message for Responsible User
    logger.success(f"Sending SLA Ping-Message...")
    asyncio.run(
        request_to_send_telegram_message(
            order_id=order_id,
            message_text=formatted_message_text,
            chat_id=telegram_chat_id,
            message_thread_id=telegram_thread_id,
        )
    )
