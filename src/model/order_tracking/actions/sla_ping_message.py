from loguru import logger

from infra.domyland.chat import get_message_template
from infra.domyland.constants import MessageTemplateName
from kafka.helpers.telegram_message_helper import request_to_send_telegram_message
from model.order_tracking.helpers.message_order_params import (
    get_order_params_for_message,
)
from model.order_tracking.helpers.telegram_chat import get_responsible_user_telegram
from scheme.order_classification.order_classification_config_scheme import (
    MessageTemplate,
    ResponsibleUser,
)
from scheme.order_classification.order_classification_scheme import OrderDetails
from scheme.order_notification.order_telegram_message_scheme import OrderTelegramMessage


async def send_sla_ping_message(
    order_details: OrderDetails,
    responsible_user: ResponsibleUser,
    messages_templates: list[MessageTemplate],
) -> OrderTelegramMessage:
    """
    Send SLA Ping-Message to Responsible User in Telegram Chat.
    """

    user_id = responsible_user.user_id

    # * Extract params for message from Order
    (
        order_id,
        crm_url,
        address,
        address_with_apartment,
        service_title,
        query,
        created_at_str,
        responsible_users_full_names,
        _,
        _,
        sla_time_text,
    ) = get_order_params_for_message(order_details=order_details)

    # * Get template for SLA ping-message
    template_name = MessageTemplateName.SLA_PING
    message_template = get_message_template(
        templates_list=messages_templates,
        template_name=template_name,
    )
    message_text = message_template.text

    # * Get Telegram of Responsible User
    telegram_username, telegram_chat_id, telegram_thread_id = (
        get_responsible_user_telegram(
            order_address=address,
            responsible_user=responsible_user,
        )
    )

    # * Format message
    formatted_message_text = message_text.format(
        telegram_username=telegram_username,
        crm_order_url=crm_url,
        address_with_apartment=address_with_apartment,
        service_title=service_title,
        query=query,
        created_at_str=created_at_str,
        responsible_users_full_names=", ".join(responsible_users_full_names),
        order_id=order_id,
        sla_time_text=sla_time_text,
    )

    logger.debug(
        f"SLA Ping-Message for Responsible User:\n"
        f"ID: {user_id}\n"
        f"Telegram Username: {telegram_username}\n"
        f"Telegram Chat ID: {telegram_chat_id}\n"
        f"Telegram Topic ID: {telegram_thread_id}\n"
        f"Message text:\n{formatted_message_text}"
    )

    # * Request Telegram message for Responsible User
    logger.success(f"Sending SLA Ping-Message...")
    message_body = await request_to_send_telegram_message(
        message_key=str(order_id),
        message_text=formatted_message_text,
        chat_id=telegram_chat_id,
        message_thread_id=telegram_thread_id,
    )
    return message_body
