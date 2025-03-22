from datetime import datetime

from infra.domyland.orders import get_order_details_by_id
from infra.order_tracking.action import OrderTrackingTaskAction
from scheme.order_classification.order_classification_scheme import OrderDetails
from scheme.order_tracking.order_tracking_task_scheme import OrderTrackingTask


def check_if_order_changed(
    order_details: OrderDetails,
    prev_order_details: OrderDetails,
) -> bool:
    # TODO: check if order not changed by params values
    return order_details == prev_order_details


def process_order_tracking_task(
    task: OrderTrackingTask,
):
    order_id = task.order_id
    order_details = get_order_details_by_id(order_id=order_id)

    # Check if Order not changed
    last_order_details = task.prev
    is_order_changed = check_if_order_changed(
        order_details=order_details,
        prev_order_details=last_order_details,
    )

    # Do nothing
    if is_order_changed:
        # TODO: skip task, update action time
        return

    action = task.next_action
    if action is None:
        return 

    action_time = task.action_time
    if action_time is not None:
        pass

    # Check if now is time to do Action
    current_time = datetime.now()
    if current_time < action_time:
        # Action time has not yet arrived, skip processing
        return

    # Do necessary Action
    if task.next_action == OrderTrackingTaskAction.FETCH_ORDER_DETAILS:
        # TODO: fetching order details
        pass
    # Update Order Status
    elif task.next_action == OrderTrackingTaskAction.UPDATE_ORDER_STATUS:
        # TODO: updating order status
        pass
    elif task.next_action == OrderTrackingTaskAction.SEND_NEW_ORDER_MESSAGE:
        # TODO: sending a new order message
        pass
    elif task.next_action == OrderTrackingTaskAction.SEND_SLA_PING_MESSAGE:
        # TODO: sending an SLA ping message
        pass
    else:
        # TODO: Handle unknown action
        raise ValueError(f"Unknown action: {task.next_action}")

    return
