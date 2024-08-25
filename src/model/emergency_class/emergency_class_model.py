import re

import requests
from fastapi import HTTPException, status

from datastep.chains.emergency_class_chain import get_emergency_class_chain
from infra.env import DOMYLAND_AUTH_EMAIL, DOMYLAND_AUTH_PASSWORD, DOMYLAND_AUTH_TENANT_NAME
from scheme.emergency_class.emergency_class_scheme import EmergencyClassRequest, SummaryType, SummaryTitle, \
    EmergencyClassResponse, AlertTypeID, OrderDetails

DOMYLAND_API_BASE_URL = "https://sud-api.domyland.ru"
DOMYLAND_APP_NAME = "Datastep"


def _normalize_resident_request_string(query: str) -> str:
    # Remove \n symbols
    removed_line_breaks_query = query.replace("\n", " ")

    # Remove photos
    removed_photos_query = removed_line_breaks_query.replace("Прикрепите фото:", " ")

    # Remove urls
    removed_urls_query = re.sub(r"http\S+", " ", removed_photos_query)

    # Replace multiple spaces with one
    fixed_spaces_query = re.sub(r"\s+", " ", removed_urls_query)

    return fixed_spaces_query


def _get_auth_token() -> str:
    response = requests.post(
        url=f"{DOMYLAND_API_BASE_URL}/auth",
        json={
            "email": DOMYLAND_AUTH_EMAIL,
            "password": DOMYLAND_AUTH_PASSWORD,
            "tenantName": DOMYLAND_AUTH_TENANT_NAME,
        },
        headers={
            "AppName": DOMYLAND_APP_NAME,
        }
    )

    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text,
        )

    auth_token = response.json()['token']
    return auth_token


def _get_domyland_headers(auth_token: str | None):
    if auth_token is None:
        return {
            "AppName": DOMYLAND_APP_NAME,
        }

    return {
        "AppName": DOMYLAND_APP_NAME,
        "Authorization": auth_token,
    }


def _get_order_details_by_id(order_id: int) -> OrderDetails:
    # Authorize in Domyland API
    auth_token = _get_auth_token()

    # Update order status
    response = requests.get(
        url=f"{DOMYLAND_API_BASE_URL}/orders/{order_id}",
        headers=_get_domyland_headers(auth_token)
    )
    response_data = response.json()

    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"OrderDetails GET: {response_data}",
        )

    order_details = OrderDetails(**response_data)
    return order_details


def _update_order_emergency_status(order_id: int, is_accident: bool):
    # Authorize in Domyland API
    auth_token = _get_auth_token()

    # Update order status
    response = requests.put(
        url=f"{DOMYLAND_API_BASE_URL}/orders/{order_id}",
        json={
            "isAccident": is_accident,
        },
        headers=_get_domyland_headers(auth_token)
    )
    response_data = response.json()

    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Order UPDATE: {response_data}",
        )

    return response_data


def get_emergency_class(body: EmergencyClassRequest) -> EmergencyClassResponse:
    # Check if order is new (created)
    if body.alertTypeId != AlertTypeID.NEW_ORDER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неверный ID типа уведомления.",
        )

    # Get order details to get resident comment
    order_id: int = body.data.orderId
    order_details = _get_order_details_by_id(order_id)

    order_query: str | None = None
    for summary in order_details.summary:
        if summary.type == SummaryType.TEXT and summary.title == SummaryTitle.COMMENT:
            order_query = summary.value

    # Check if resident comment exists
    if order_query is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"В заявке {order_id} отсутствует комментарий для определения её аварийности.",
        )

    # Get order emergency
    normalized_query = _normalize_resident_request_string(order_query)
    chain = get_emergency_class_chain()
    order_emergency: str = chain.run(query=normalized_query)
    is_accident = order_emergency.lower().strip() == "аварийная"

    # Update order emergency class in Domyland
    update_order_response_data = None
    if is_accident:
        update_order_response_data = _update_order_emergency_status(
            order_id=order_id,
            is_accident=is_accident,
        )

    return EmergencyClassResponse(
        order_id=order_id,
        order_query=order_query,
        is_accident=is_accident,
        order_emergency=order_emergency,
        order_update_response=update_order_response_data,
    )

# [
#     'Поле \"serviceId\" обязательно для заполнения',
#     'Поле \"Объект\" обязательно для заполнения',
#     'Поле \"eventId\" обязательно для заполнения',
#     'Поле \"orderData\" обязательно для заполнения'
# ]
