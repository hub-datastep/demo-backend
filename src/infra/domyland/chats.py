import requests
from fastapi import HTTPException

from infra.domyland.auth import (
    get_ai_account_auth_token,
    get_domyland_headers,
    get_public_account_auth_token,
)
from infra.domyland.constants import (
    DOMYLAND_API_BASE_URL,
    ORDER_CLIENT_CHAT_TARGET_TYPE_ID,
)


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
    message: str,
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
        "text": message,
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
