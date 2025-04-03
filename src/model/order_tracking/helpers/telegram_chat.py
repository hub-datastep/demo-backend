from fastapi import HTTPException, status

from scheme.order_classification.order_classification_config_scheme import (
    ResponsibleUser,
    TelegramChat,
)


def get_telegram_chat_by_order_address(
    chats_list: list[TelegramChat] | None,
    order_address: str,
) -> TelegramChat:
    """
    Get Telegram Chat by Order address. Raise error if not found.
    """

    # Check if Chats exist
    if not chats_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No chats available to search for the order address.",
        )

    # Get Chat by Order address
    for chat in chats_list:
        # Skip disabled Chat
        if chat.is_disabled:
            continue

        address_list = chat.address_list

        # Check if addresses exist
        if not address_list:
            continue

        # Check if address list contains Order address
        for address in address_list:
            if address.lower() in order_address.lower():
                return chat

    # If Chat not found, raise error
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Telegram Chat not found for Order with address '{order_address}'",
    )


def get_responsible_user_telegram(
    order_address: str,
    responsible_user: ResponsibleUser,
) -> tuple[str, str, int | None]:
    """
    Get Telegram params from Responsible User and Order address.
    """

    user_id = responsible_user.user_id
    telegram_user = responsible_user.telegram

    # * Check if Responsible User has Telegram
    if not telegram_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Telegram not set for Responsible user with ID '{user_id}'",
        )

    telegram_username = telegram_user.username

    # * Check if Telegram username exists
    if not telegram_username.strip():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Responsible user with ID '{user_id}' "
                "has no telegram username, cannot send message"
            ),
        )

    # * Get Telegram Chat for Responsible User by Order address
    chats_list = telegram_user.chats
    telegram_chat = get_telegram_chat_by_order_address(
        chats_list=chats_list,
        order_address=order_address,
    )
    telegram_chat_id = telegram_chat.chat_id
    telegram_thread_id = telegram_chat.thread_id

    # * Check if Telegram Chat ID exists
    if not telegram_chat_id.strip():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Responsible user with ID '{user_id}' "
                "has no telegram chat ID, cannot send message"
            ),
        )

    return telegram_username, telegram_chat_id, telegram_thread_id
