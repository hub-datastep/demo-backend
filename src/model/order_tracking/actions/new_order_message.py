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
from scheme.order_notification.order_telegram_message_scheme import OrderTelegramMessage
from util.seconds_to_time_str import get_time_str_from_seconds


async def send_new_order_message(
    order_id: int,
    order_address: str | None,
    order_address_with_apartment: str | None,
    order_serviceTitle: str | None,
    order_query: str | None,
    order_createdAt_time_str: str | None,
    order_responsible_users_full_names: list[str | None],
    responsible_user: ResponsibleUser,
    messages_templates: list[MessageTemplate],
    sla_left_time_in_sec: int,
) -> OrderTelegramMessage:
    """
    Send New Order Message to Responsible User in Telegram Chat.
    order_address - нужен для получения юзера по объекту
    order_address_with_apartment - нужен для вывода адреса с квартирой в сообщение в тг
    """

    # Преобразование параметров в пустую строку, если они равны None
    order_address = order_address or ""
    order_address_with_apartment = order_address_with_apartment or ""
    order_serviceTitle = order_serviceTitle or ""
    order_query = order_query or ""
    order_createdAt_time_str = order_createdAt_time_str or ""
    formatted_user_full_names: list[str] = [
        full_name or "" for full_name in order_responsible_users_full_names
    ]

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

    # * Get SLA time text
    # Отдаем просто "4 часа" если не просрочено, и отдаем строку "просрочен на 4 часа" если просрочен
    # в темплейте сообщения перед этой переменной будет стоять "⏰ SLA выполнения -"
    sla_time_str = get_time_str_from_seconds(seconds=abs(sla_left_time_in_sec))
    if sla_left_time_in_sec > 0:
        sla_time_text = sla_time_str
    else:
        sla_time_text = f"просрочен на {sla_time_str}"

    # * Format message
    formatted_message_text = message_text.format(
        telegram_username=telegram_username,
        crm_order_url=crm_order_url,
        order_address_with_apartment=order_address_with_apartment,
        order_serviceTitle=order_serviceTitle,
        order_query=order_query,
        order_createdAt_time_str=order_createdAt_time_str,
        order_responsible_users_full_names=", ".join(formatted_user_full_names),
        order_id=order_id,
        sla_time_text=sla_time_text,
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
    message_body = await request_to_send_telegram_message(
        message_key=str(order_id),
        message_text=formatted_message_text,
        chat_id=telegram_chat_id,
        message_thread_id=telegram_thread_id,
    )
    return message_body
