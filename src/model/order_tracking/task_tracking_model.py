from datetime import datetime

from sqlmodel import Session

from infra.domyland.constants import OrderStatusID
from infra.domyland.orders import get_order_details_by_id
from infra.order_tracking.action import OrderTrackingTaskAction
from infra.order_tracking.task_status import OrderTrackingTaskStatus
from repository.order_tracking import order_tracking_task_repository
from scheme.order_classification.order_classification_scheme import OrderDetails
from scheme.order_tracking.order_tracking_task_scheme import (
    OrderTrackingTask,
    OrderTrackingTaskActinLog,
)
from util.dates import get_now_utc
from util.json_serializing import serialize_obj


def check_if_order_changed(
    order_details: OrderDetails,
    prev_order_details: OrderDetails | None = None,
) -> bool:
    """
    Compare params from `order_details` with params from `prev_order_details`
    to check if order changed.

    Params to compare:
    - ...
    """

    # If no prev details, so order chaged
    if not prev_order_details:
        return True

    # TODO: check if order not changed by params values
    return order_details == prev_order_details


def mark_task_as_completed(
    session: Session,
    task: OrderTrackingTask,
) -> OrderTrackingTask:
    """
    Mark task as completed and stop tracking it.
    """

    # Update necessary params for completed Task
    task.internal_status = OrderTrackingTaskStatus.COMPLETED
    task.next_action = None
    task.action_time = None
    task.is_completed = True
    task.finished_at = get_now_utc()

    # Update Task
    updated_task = order_tracking_task_repository.update(
        session=session,
        task=task,
    )

    return updated_task


def process_order_tracking_task(
    session: Session,
    task: OrderTrackingTask,
):
    # * Get Order details
    order_id = task.order_id
    order_details = get_order_details_by_id(order_id=order_id)

    # * Check if Order changed
    is_order_changed: bool = False
    if task.last_order_details:
        last_order_details = OrderDetails(**task.last_order_details)
        is_order_changed = check_if_order_changed(
            order_details=order_details,
            prev_order_details=last_order_details,
        )

    # * Order changed, so do nothing
    if is_order_changed:
        # Check if Order Status changed to "Completed"
        if order_details.order.orderStatusId == OrderStatusID.COMPLETED:
            mark_task_as_completed(
                session=session,
                task=task,
            )
            return

        # TODO: skip task, update action time
        return

    action = task.next_action
    if action is None:
        # TODO: Set action for recently created task
        return

    action_time = task.action_time
    if action_time is None:
        # TODO: Set time for task action
        return

    # TODO: Check if now is time to do Action
    current_time = get_now_utc()
    if current_time < action_time:
        # Action time has not yet arrived, skip processing
        return

    # Do necessary Action
    action_log = OrderTrackingTaskActinLog()
    # * Update Order Details in Task
    if action == OrderTrackingTaskAction.FETCH_ORDER_DETAILS:
        task.last_order_details = serialize_obj(order_details)
        action_log.name = OrderTrackingTaskAction.FETCH_ORDER_DETAILS
        action_log.started_at = current_time

    # * Update Order Status
    elif action == OrderTrackingTaskAction.UPDATE_ORDER_STATUS:
        # TODO: updating order status
        pass

    # * Send Message about new Order
    elif action == OrderTrackingTaskAction.SEND_NEW_ORDER_MESSAGE:
        # TODO: send new-order message
        pass

    # * Send Ping-Message about SLA
    elif action == OrderTrackingTaskAction.SEND_SLA_PING_MESSAGE:
        # TODO: send SLA ping-message
        pass

    else:
        # TODO: Handle unknown action
        raise ValueError(f"Unknown action: {action}")

    # * Add new log to task actions logs list if action was done
    if action_log.name:
        action_log.finished_at = get_now_utc()

        if task.actions_logs:
            task.actions_logs.append(action_log)
        else:
            task.actions_logs = [action_log]

    # TODO: Update Task

    return action_log
