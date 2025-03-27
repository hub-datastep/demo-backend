import traceback
from datetime import datetime, timedelta

from fastapi import HTTPException
from loguru import logger
from sqlmodel import Session

from infra.domyland.constants import OrderStatusID
from infra.domyland.orders import (
    get_order_details_by_id,
    get_responsible_users_by_config_ids,
)
from infra.env import env
from infra.order_tracking.action import TIME_DEPENDENT_ACTIONS, OrderTrackingTaskAction
from infra.order_tracking.task_status import OrderTrackingTaskStatus
from model.order_tracking.actions.new_order_message import send_new_order_message
from model.order_tracking.actions.sla_ping_message import send_sla_ping_message
from repository.order_tracking import order_tracking_task_repository
from scheme.order_classification.order_classification_config_scheme import (
    MessageTemplate,
    ResponsibleUser,
)
from scheme.order_classification.order_classification_scheme import OrderDetails
from scheme.order_tracking.order_tracking_task_scheme import (
    OrderTrackingTask,
    OrderTrackingTaskActinLog,
)
from util.dates import get_now_utc
from util.json_serializing import serialize_obj

# For DEV
SLA_PING_PERIOD_IN_MIN_DEV = 1
# For PROD
SLA_PING_PERIOD_IN_MIN_PROD = 60

SLA_PING_PERIOD_IN_MIN = (
    SLA_PING_PERIOD_IN_MIN_DEV if env.IS_DEV_ENV else SLA_PING_PERIOD_IN_MIN_PROD
)


def check_if_order_changed(
    order_details: OrderDetails,
    prev_order_details: OrderDetails | None = None,
) -> tuple[bool, bool]:
    """
    Compare params from `order_details` with params from `prev_order_details`
    to check if order changed.

    Params to compare:
    - Order Status ID
    - Responsible Users

    Returns:
    - Is Responsible Users changed
    - Is Order Status changed
    """

    # If no prev details, so all params changed
    if not prev_order_details:
        return True, True

    # Check if Responsible Users changed
    responsible_users_ids = {user.id for user in order_details.order.responsibleUsers}
    prev_responsible_users_ids = {
        user.id for user in prev_order_details.order.responsibleUsers
    }
    # TODO: check if responsible_users_ids includes TRANSFER_ACCOUNT_ID -> responsible users not chaged
    is_responsible_users_changed = responsible_users_ids != prev_responsible_users_ids

    # Check if Responsible Users changed
    order_status_id = order_details.order.orderStatusId
    prev_order_status_id = prev_order_details.order.orderStatusId
    is_order_status_changed = order_status_id != prev_order_status_id

    return is_responsible_users_changed, is_order_status_changed


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
    try:
        # * Update Task Internal Status
        task.internal_status = OrderTrackingTaskStatus.TRACKING
        order_tracking_task_repository.update(
            session=session,
            task=task,
        )

        config = task.config

        # * Get Order details
        order_id = task.order_id
        logger.debug(f"Fetching details of Order with ID {order_id}..")
        order_details = get_order_details_by_id(order_id=order_id)
        order = order_details.order

        # ? Check if Order changed
        # last_order_details = (
        #     OrderDetails(**task.last_order_details) if task.last_order_details else None
        # )
        # is_responsible_users_changed, is_order_status_changed = check_if_order_changed(
        #     order_details=order_details,
        #     prev_order_details=last_order_details,
        # )

        # ? Order changed, so do nothing
        # if is_order_status_changed:

        # * Check if Order Status changed to "Completed"
        is_order_completed = order.orderStatusId == OrderStatusID.COMPLETED
        if is_order_completed:
            logger.success(f"Order with ID {order_id} is Completed")
            mark_task_as_completed(
                session=session,
                task=task,
            )
            return

        action = task.next_action
        if action is None:
            # TODO: Set action for recently created task
            raise Exception(f"Task of Order with ID {order_id} has no action")

        current_time = get_now_utc()
        current_timestamp = int(current_time.timestamp())
        action_log = OrderTrackingTaskActinLog()

        # * ############################ * #
        # *  Not time-dependent Actions  * #
        # * ############################ * #
        logger.debug(f"Task of Order with ID {order_id} has action '{action}'")
        if action not in TIME_DEPENDENT_ACTIONS:
            # * Update Order Details in Task
            if action == OrderTrackingTaskAction.FETCH_ORDER_DETAILS:
                task.last_order_details = serialize_obj(order_details)
                action_log.name = OrderTrackingTaskAction.FETCH_ORDER_DETAILS
                action_log.started_at = current_time

                # Set next-action as SEND_NEW_ORDER_MESSAGE
                task.next_action = OrderTrackingTaskAction.SEND_NEW_ORDER_MESSAGE
                # Set Internal Status to PENDING
                task.internal_status = OrderTrackingTaskStatus.PENDING

            # * Send Message about new Order
            elif action == OrderTrackingTaskAction.SEND_NEW_ORDER_MESSAGE:
                # ! Order must have any Responsible User
                # Get Responsible Users
                config_responsible_users = [
                    ResponsibleUser(**user) for user in config.responsible_users
                ]
                responsible_users = get_responsible_users_by_config_ids(
                    order_responsible_users=order.responsibleUsers,
                    config_responsible_users=config_responsible_users,
                )
                if responsible_users:
                    # Send new Order Message
                    templates_list = [
                        MessageTemplate(**template)
                        for template in config.messages_templates
                    ]
                    logger.success(f"Sending new Order Message...")
                    send_new_order_message(
                        order_id=order_id,
                        responsible_users_list=responsible_users,
                        messages_templates=templates_list,
                    )

                    # Set next action as SEND_SLA_PING_MESSAGE
                    task.next_action = OrderTrackingTaskAction.SEND_SLA_PING_MESSAGE
                    # Set Internal Status to WAITING_ACTION_TIME
                    task.internal_status = OrderTrackingTaskStatus.WAITING_ACTION_TIME
                    # Set action time as half of solve SLA left
                    sla_solve_timestamp = order.solveTimeSLA
                    logger.debug(f"SLA Solve Timestamp: {sla_solve_timestamp}")
                    if sla_solve_timestamp:
                        sla_solve_time_in_sec = sla_solve_timestamp - current_timestamp
                        sla_ping_datetime = datetime.fromtimestamp(
                            timestamp=current_timestamp + sla_solve_time_in_sec / 2
                        )
                        logger.debug(f"Next SLA ping datetime: {sla_ping_datetime}")
                        task.action_time = sla_ping_datetime
                else:
                    raise Exception(
                        f"Order with ID {order_id} has no Responsible Users, "
                        "so do not send message"
                    )

        # * ######################## * #
        # *  Time-dependent Actions  * #
        # * ######################## * #
        else:
            # Check if action time exists
            action_time = task.action_time
            if action_time is not None:
                action_time = action_time.astimezone(current_time.tzinfo)
            else:
                raise Exception(
                    f"Task of Order with ID {order_id} has action '{action}', "
                    "but has no time to run it"
                )

            # Check if now is time to do Action
            if action_time and current_time >= action_time:
                # * Send Ping-Message about SLA
                if action == OrderTrackingTaskAction.SEND_SLA_PING_MESSAGE:
                    # ! Order must have any Responsible User
                    # Get Responsible Users
                    config_responsible_users = [
                        ResponsibleUser(**user) for user in config.responsible_users
                    ]
                    responsible_users = get_responsible_users_by_config_ids(
                        order_responsible_users=order.responsibleUsers,
                        config_responsible_users=config_responsible_users,
                    )
                    if responsible_users:
                        # Send SLA Ping-Message
                        templates_list = [
                            MessageTemplate(**template)
                            for template in config.messages_templates
                        ]
                        logger.success(f"Sending SLA Ping-Message...")
                        sla_solve_timestamp = order.solveTimeSLA
                        sla_solve_time_in_sec = sla_solve_timestamp - current_timestamp
                        send_sla_ping_message(
                            order_id=order_id,
                            responsible_users_list=responsible_users,
                            messages_templates=templates_list,
                            sla_time_left_in_sec=sla_solve_time_in_sec,
                        )

                        # Set next action as SEND_SLA_PING_MESSAGE
                        task.next_action = OrderTrackingTaskAction.SEND_SLA_PING_MESSAGE
                        # Set Internal Status to WAITING_ACTION_TIME
                        task.internal_status = (
                            OrderTrackingTaskStatus.WAITING_ACTION_TIME
                        )
                        # Set next action time as Now Time + SLA_PING_PERIOD_IN_MIN
                        task.action_time = get_now_utc() + timedelta(
                            minutes=SLA_PING_PERIOD_IN_MIN,
                        )
                    else:
                        raise Exception(
                            f"Order with ID {order_id} has no Responsible Users, "
                            "so do not send message"
                        )

    # * Errors Handling
    except (HTTPException, Exception) as error:
        action_log.is_error = True
        task.internal_status = OrderTrackingTaskStatus.FAILED

        # Получаем текст ошибки из атрибута detail для HTTPException
        if isinstance(error, HTTPException):
            comment = error.detail
        # Для других исключений используем str(error)
        else:
            logger.error(traceback.format_exc())
            comment = str(error)

        log_metadatas = {
            "comment": f"{comment}",
        }

        # Save error to metadatas
        if action_log.metadatas:
            action_log.metadatas.update(log_metadatas)
        else:
            action_log.metadatas = log_metadatas

        # Print error to logs
        logger.error(comment)

    logger.debug(
        f"Next action for Task of Order with ID {order_id} "
        f"is '{task.next_action}' at {task.action_time}"
    )

    # * Add new log to task actions logs list if action was done
    if action_log.name:
        action_log.finished_at = get_now_utc()
        action_log_dict = serialize_obj(action_log)

        if task.actions_logs:
            task.actions_logs.append(action_log_dict)
        else:
            task.actions_logs = [action_log_dict]

    # * Update Task
    order_tracking_task_repository.update(
        session=session,
        task=task,
    )
