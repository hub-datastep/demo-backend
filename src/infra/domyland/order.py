import requests
from aiohttp.hdrs import METH_POST
from fastapi import HTTPException, status

from infra.domyland.auth import (
    get_ai_account_auth_token,
    get_ai_account_auth_token_async,
    get_domyland_headers,
)
from infra.domyland.base import Domyland
from infra.domyland.constants import DOMYLAND_API_BASE_URL, DOMYLAND_CRM_BASE_URL
from scheme.order_classification.order_classification_config_scheme import (
    ResponsibleUser,
)
from scheme.order_classification.order_classification_scheme import (
    OrderDetails,
    OrderResponsibleUser,
    OrderSummaryValue,
    SummaryTitle,
)


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


async def get_order_details_by_id_async(order_id: int) -> OrderDetails:
    """
    Fetch all Order data by ID from Domyland.
    """

    # Authorize in Domyland API
    await get_ai_account_auth_token_async()

    # Get order details
    endpoint = f"initial-data/dispatcher/order-info/{order_id}"
    response_data = await Domyland.request(
        method=METH_POST,
        endpoint=endpoint,
    )
    # logger.debug(f"Order {order_id} details:\n{response_data}")

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
    raise_error_if_not_found: bool | None = False,
) -> OrderSummaryValue | None:
    """
    Extract param by name from Order details.
    """

    order = order_details.order
    order_id = order.id

    # Search param in Order
    keyword = param_name.lower().strip()
    for param in order.summary:
        if param.title and keyword in param.title.lower().strip():
            return param.value

    # If enabled, raise Error if param not found
    if raise_error_if_not_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} has no '{param_name}'",
        )


def get_query_from_order_details(
    order_details: OrderDetails,
    raise_error_if_not_found: bool | None = False,
) -> str | None:
    """
    Extract Resident query from Order details.
    """

    # Get resident query from Order
    order_query: str | None = get_param_by_name_from_order_details(
        order_details=order_details,
        param_name=SummaryTitle.COMMENT,
        raise_error_if_not_found=raise_error_if_not_found,
    )

    return order_query


def get_address_from_order_details(
    order_details: OrderDetails,
    raise_error_if_not_found: bool | None = False,
) -> str | None:
    """
    Extract Order address from Order details.

    e.g. "Корабельная ул, д. 1".
    """

    # Get resident address (object)
    order_address: str | None = get_param_by_name_from_order_details(
        order_details=order_details,
        param_name=SummaryTitle.OBJECT,
        raise_error_if_not_found=raise_error_if_not_found,
    )

    return order_address


def get_address_with_apartment_from_order_details(
    order_details: OrderDetails,
    raise_error_if_not_found: bool | None = False,
) -> str | None:
    """
    Extract Order address with apartment from Order details.

    e.g. "Корабельная ул, д. 1 кв 521".
    """

    # Get resident address with apartment
    order_address_with_apartment: str | None = get_param_by_name_from_order_details(
        order_details=order_details,
        param_name=SummaryTitle.ADDRESS,
        raise_error_if_not_found=raise_error_if_not_found,
    )

    return order_address_with_apartment


def get_responsible_users_by_config_ids(
    order_responsible_users: list[OrderResponsibleUser] | None = None,
    config_responsible_users: list[ResponsibleUser] | None = None,
) -> None | list[ResponsibleUser]:
    """
    Map Responsible Users from Order with Users from Config.
    """

    # Check if Responsible Users exist in Order and in Config
    if not order_responsible_users or not config_responsible_users:
        return None

    # Map Responsible Users from Order with Users from Config
    found_responsible_users: list[ResponsibleUser] = []
    for user_in_order in order_responsible_users:
        for user_in_config in config_responsible_users:
            if str(user_in_order.id) == user_in_config.user_id:
                found_responsible_users.append(user_in_config)

    return found_responsible_users


# if __name__ == "__main__":
#     # Test Order
#     order_id = 3197122
#     # Real Order with Photos from Cleaning Account
#     order_id = 3198517
#     # order_id = 3333919
#     # order_id = 3334010

#     order_details = get_order_details_by_id(order_id)
#     # logger.debug(f"Order {order_id} details: {order_details}")
