import asyncio
import time

import requests
from aiohttp.hdrs import METH_PUT
from fastapi import HTTPException
from loguru import logger

from infra.domyland.auth import (
    get_ai_account_auth_token,
    get_ai_account_auth_token_async,
    get_domyland_headers,
)
from infra.domyland.base import Domyland
from infra.domyland.constants import DOMYLAND_API_BASE_URL
from infra.order_classification import WAIT_TIME_IN_SEC
from scheme.order_notification.order_notification_scheme import OrderStatusDetails


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


async def update_order_status_details_async(
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
        await get_ai_account_auth_token_async()

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
        response_data = await Domyland.request(
            method=METH_PUT,
            endpoint=f"orders/{order_id}/status",
            json=req_body,
        )

        return response_data, req_body

    except Exception as e:
        error_str = str(e)
        logger.error(
            f"Error occurred while updating order with ID {order_id}: {error_str}"
        )
        logger.error(f"Wait {WAIT_TIME_IN_SEC} sec and try again..")
        await asyncio.sleep(WAIT_TIME_IN_SEC)

        logger.error(f"Timeout passed, try update order with ID {order_id} again")
        return await update_order_status_details_async(
            order_id=order_id,
            responsible_dept_id=responsible_dept_id,
            order_status_id=order_status_id,
            responsible_users_ids=responsible_users_ids,
            inspector_users_ids=inspector_users_ids,
        )
