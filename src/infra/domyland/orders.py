import time

import requests
from fastapi import HTTPException, status
from loguru import logger

from infra.domyland.auth import get_ai_account_auth_token, get_domyland_headers
from infra.domyland.constants import DOMYLAND_API_BASE_URL, DOMYLAND_CRM_BASE_URL
from infra.order_classification import WAIT_TIME_IN_SEC
from scheme.order_classification.order_classification_config_scheme import (
    ResponsibleUser,
)
from scheme.order_classification.order_classification_scheme import (
    OrderDetails,
    OrderResponsibleUser,
    SummaryTitle,
)
from scheme.order_notification.order_notification_scheme import OrderStatusDetails
from util.format_timestamp_to_human_readable import format_timestamp_to_human_readable
from util.validation import is_exists_and_not_empty


def get_crm_order_url(order_id: int) -> str:
    url = f"{DOMYLAND_CRM_BASE_URL}/{order_id}"
    return url


def get_order_details_by_id(order_id: int) -> OrderDetails:
    """
    Fetch all Order data by ID from Domyland.
    """

    # Authorize in Domyland API
    auth_token = get_ai_account_auth_token()

    # Get order details
    request_url = (
        f"{DOMYLAND_API_BASE_URL}/initial-data/dispatcher/order-info/{order_id}"
    )
    response = requests.get(
        url=request_url,
        headers=get_domyland_headers(auth_token),
    )
    response_data = response.json()
    # logger.debug(f"Order {order_id} details:\n{response_data}")

    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"OrderDetails GET: {response_data}",
        )

    # ! DEBUG ONLY
    # * Just to save all order data to json-file
    # * Uncomment this if you need to save all response data
    # with open(f"order-{order_id}-details.json", "w", encoding="utf-8") as f:
    #     import json

    #     json.dump(response_data, f, ensure_ascii=False)

    order_details = OrderDetails(**response_data)
    return order_details


def get_param_by_name_from_order_details(
    order_details: OrderDetails,
    param_name: str,
) -> str | None:
    """
    Extract param by name from Order details.
    """

    keyword = param_name.lower().strip()
    param_value: str | None = None
    for param in order_details.order.summary:
        # Search comment param
        if param.title and keyword in param.title.lower().strip():
            param_value = param.value
            break

    return param_value


def get_query_from_order_details(
    order_id: int,
    order_details: OrderDetails,
) -> str | None:
    """
    Extract Resident query from Order details. Raise error if not found or empty.
    """

    # Get resident order query
    order_query = get_param_by_name_from_order_details(
        order_details=order_details,
        param_name=SummaryTitle.COMMENT,
    )

    # * Check if resident comment exists and not empty if enabled
    if not is_exists_and_not_empty(order_query):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Order with ID {order_id} has no comment",
        )

    return order_query


def get_address_from_order_details(
    order_id: int,
    order_details: OrderDetails,
) -> str | None:
    """
    Extract Order address from Order details. Raise error if not found or empty.
    Пример адреса объекта - "Корабельная ул, д. 1"
    Похожая функция, получающая более точную информацию - get_address_with_apartment_from_order_details
    """

    # Get resident address (object)
    order_address = get_param_by_name_from_order_details(
        order_details=order_details,
        param_name=SummaryTitle.OBJECT,
    )

    # * Check if resident address exists and not empty if enabled
    if not is_exists_and_not_empty(order_address):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Order with ID {order_id} has no address",
        )

    return order_address


def get_address_with_apartment_from_order_details(
    order_id: int,
    order_details: OrderDetails,
) -> str | None:
    """
    Extract Order address from Order details. Raise error if not found or empty.
    Пример адреса с квартирой - "Корабельная ул, д. 1 кв 521"
    """

    # Get resident address (object)
    order_address_with_apartment = get_param_by_name_from_order_details(
        order_details=order_details,
        param_name=SummaryTitle.ADDRESS,
    )

    # * Пока решил не рейзить эксепшн, чтобы не прерывать процесс сбора данных для заявки, потому что поле не обязательное
    # if not is_exists_and_not_empty(order_address_with_apartment):
    #     raise HTTPException(
    #         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #         detail=f"Order with ID {order_id} has no address with apartment",
    #     )

    return order_address_with_apartment


def get_responsible_users_by_config_ids(
    order_responsible_users: list[OrderResponsibleUser] | None = None,
    config_responsible_users: list[ResponsibleUser] | None = None,
) -> None | list[ResponsibleUser]:
    if not order_responsible_users or not config_responsible_users:
        return None

    found_responsible_users: list[ResponsibleUser] = []
    for user_in_order in order_responsible_users:
        for user_in_config in config_responsible_users:
            if str(user_in_order.id) == user_in_config.user_id:
                found_responsible_users.append(user_in_config)

    return found_responsible_users


def get_responsible_users_full_names_by_order_id(
    order_id: int,
) -> list[str | None]:
    """
    Fetch full names of responsible users for a given order ID.
    Raise an HTTPException if responsible users are not found.
    Пример массива фулл неймов юзеров из заявки - ['Специалист Александр ', 'Клининг Рпм-Четыре ']
    """
    try:
        order_status_details = get_order_status_details_by_id(order_id)

        # Проверяем, что responsibleUsers не является None
        if order_status_details.responsibleUsers is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} has no responsible users.",
            )

        # Создаем массив для хранения fullName пользователей
        user_full_names = [user.fullName for user in order_status_details.responsibleUsers]

        return user_full_names

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching responsible users for order ID {order_id}: {str(e)}",
        )


def get_order_status_details_by_id(order_id: int) -> OrderStatusDetails:
    # Authorize in Domyland API
    auth_token = get_ai_account_auth_token()

    # Update responsible user
    response = requests.get(
        url=f"{DOMYLAND_API_BASE_URL}/orders/{order_id}/status",
        headers=get_domyland_headers(auth_token),
    )
    response_data = response.json()

    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"OrderStatusDetails GET: {response_data}",
        )

    # ! DEBUG ONLY
    # * Just to save all order data to json-file
    # * Uncomment this if you need to save all response data
    # with open(f"order-{order_id}-status-details.json", "w", encoding="utf-8") as f:
    #     import json

    #     json.dump(response_data, f, ensure_ascii=False)

    order_status_details = OrderStatusDetails(**response_data)
    return order_status_details


def update_order_status_details(
    order_id: int,
    responsible_dept_id: int,
    order_status_id: int,
    responsible_users_ids: list[int],
    inspector_users_ids: list[int],
    prev_status_comment: str | None = None,
) -> tuple[dict, dict]:
    try:
        # # Just save prev params in order status details
        # prev_order_status_details = _get_order_status_details(order_id)

        # TODO: save prev order status details when update params

        # Authorize in Domyland API
        auth_token = get_ai_account_auth_token()

        req_body = {
            # # Save all prev params from order status details (not needed to update)
            # **prev_order_status_details,
            # Update necessary params
            "responsibleDeptId": responsible_dept_id,
            "orderStatusId": order_status_id,
            "responsibleUserIds": responsible_users_ids,
            "inspectorIds": inspector_users_ids,
            "orderStatusComment": prev_status_comment,
        }

        # Update responsible user
        response = requests.put(
            url=f"{DOMYLAND_API_BASE_URL}/orders/{order_id}/status",
            json=req_body,
            headers=get_domyland_headers(auth_token),
        )
        response_data = response.json()

        if not response.ok:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Order status UPDATE: {response_data}",
            )

        return response_data, req_body

    except Exception as e:
        error_str = str(e)
        logger.error(
            f"Error occurred while updating order with ID {order_id}: {error_str}"
        )
        logger.error(f"Wait {WAIT_TIME_IN_SEC} sec and try again..")
        time.sleep(WAIT_TIME_IN_SEC)

        logger.error(f"Timeout passed, try update order with ID {order_id} again")
        return update_order_status_details(
            order_id=order_id,
            responsible_dept_id=responsible_dept_id,
            order_status_id=order_status_id,
            responsible_users_ids=responsible_users_ids,
            inspector_users_ids=inspector_users_ids,
        )


# if __name__ == "__main__":
    # Test Order
    # order_id = 3197122
    # Real Order with Photos from Cleaning Account
    # order_id = 3198517
    # # order_id = 3333919
    # # order_id = 3334010

    # order_details = get_order_details_by_id(order_id)
    # # logger.debug(f"Order {order_id} details: {order_details}")

    # order_createdAt = order_details.order.createdAt
    # logger.debug(f"Order {order_id} createdAt: {order_createdAt}")
    # order_timestamp=format_timestamp_to_human_readable(order_createdAt)
    # logger.debug(f"Order {order_id} format_timestamp_to_human_readable: {order_timestamp}")

    # order_serviceTitle = order_details.order.serviceTitle
    # logger.debug(f"Order {order_id} serviceTitle: {order_serviceTitle}")

    # order_query = get_query_from_order_details(
    #     order_id=order_id,
    #     order_details=order_details,
    # )
    # logger.debug(f"Order {order_id} query: {order_query}")

    # order_responsible_users_full_names = get_responsible_users_full_names_by_order_id(
    #     order_id=order_id,
    # )
    # logger.debug(
    #     f"Order {order_id} responsible users full names: {order_responsible_users_full_names}"
    # )

    # order_address_with_apartment = get_address_with_apartment_from_order_details(
    #     order_id=order_id,
    #     order_details=order_details,
    # )
    # logger.debug(f"Order {order_id} address with apartment: {order_address_with_apartment}")