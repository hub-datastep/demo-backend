from fastapi import HTTPException, status

from infra.domyland.constants import AlertTypeID, TRANSFER_ACCOUNT_ID, OrderStatusID
from infra.domyland.orders import get_order_details_by_id
from model.order_classification.order_classification_config_model import (
    get_order_classification_default_config,
)
from scheme.order_classification.order_classification_config_scheme import (
    ResponsibleUser,
)
from scheme.order_notification.order_notification_scheme import (
    OrderNotificationRequestBody,
)


def _get_responsible_users_by_order_class(
    responsible_users: list[ResponsibleUser],
    order_class: str,
) -> list[ResponsibleUser]:
    """
    Filter Responsible Users list by Order Class.
    """

    filtered_users = []

    for user in responsible_users:
        if user.order_class == order_class and not user.is_disabled:
            filtered_users.append(user)

    return filtered_users


def process_event(
    body: OrderNotificationRequestBody,
    client: str | None = None,
):
    alert_id = body.alertId
    alert_type_id = body.alertTypeId
    alert_timestamp = body.timestamp

    order_id = body.data.orderId
    order_status_id = body.data.orderStatusId

    # Check if event type is "order status updated"
    if alert_type_id != AlertTypeID.ORDER_STATUS_UPDATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Order with ID {order_id} has alert type ID {alert_type_id}, "
                f"but status ID {AlertTypeID.ORDER_STATUS_UPDATED} required"
            ),
        )

    config = get_order_classification_default_config(
        client=client,
    )

    # Get order details
    order_details = get_order_details_by_id(order_id=order_id)

    # Check if order status is "pending" ("Ожидание")
    is_order_in_pending_status = order_status_id == OrderStatusID.PENDING

    # Check if order responsible users include "Александр Специалист"
    # or include cleaning account
    is_transfer_account_in_responsible_users = False
    is_cleaning_account_in_responsible_users = False
    order_responsible_users = order_details.order.responsibleUsers
    for user in order_responsible_users:
        if user.id == TRANSFER_ACCOUNT_ID:
            is_transfer_account_in_responsible_users = True
            break
        if "клининг" in user.fullName:
            is_cleaning_account_in_responsible_users = True
            break

    # Check if order status comment exists
    order_status_comment = order_details.order.orderStatusComment
    is_status_comment_exists = (
        order_status_comment is not None and order_status_comment.strip() != ""
    )

    # Check in order history if cleaning account was in responsible users
    is_cleaning_account_was_in_responsible_users = False
    order_history = order_details.order.statusHistory
    for record in order_history:
        for user in record.responsibleUsers:
            if "клининг" in user.fullName:
                is_cleaning_account_was_in_responsible_users = True
                break

    # Check if cleaning-order is finished
    is_cleaning_order_finished = (
        is_order_in_pending_status
        and (
            is_cleaning_account_in_responsible_users
            or is_cleaning_account_was_in_responsible_users
        )
        and (is_transfer_account_in_responsible_users or is_status_comment_exists)
    )

    # Check if order has pinned files from Responsible Users
    order_files = order_details.order.files
    is_files_exists = order_files is not None and len(order_files) > 0

    # TODO: do actions for "cleaning-order finished"

    return
