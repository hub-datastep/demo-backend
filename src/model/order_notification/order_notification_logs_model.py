from model.order_classification.order_classification_history_model import (
    check_client_validation,
)
from repository.order_notification.order_notification_logs_repository import (
    get_log_record_by_order_id,
    save_log_record,
    update_log_record,
)
from scheme.order_notification.order_notification_logs_scheme import (
    OrderNotificationLog,
)


def get_saved_log_record_by_order_id(
    order_id: int,
    client: str | None = None,
) -> OrderNotificationLog | None:
    client = check_client_validation(client)

    saved_record = get_log_record_by_order_id(
        order_id=order_id,
        client=client,
    )
    return saved_record


def check_if_action_was_unsuccessful(
    action_name: str,
    log_record: OrderNotificationLog,
) -> bool:
    action_name = action_name.strip().lower()
    for log in log_record.actions_logs:
        # Check action name
        log_action_name: str | None = log.get("action")
        if not log_action_name or log_action_name.strip().lower() != action_name:
            continue

        # Check action metadata
        log_metadata: dict | None = log.get("metadata")
        if not log_metadata:
            return True

        # Check action response
        action_response: dict | str | None = log_metadata.get("response")
        if not action_response or not isinstance(action_response, dict):
            return True

        # Check if action finished with error
        was_error: bool | None = action_response.get("error")
        return was_error is not False

    # If actions not found
    return True


def save_order_notification_log_record(
    log_record: OrderNotificationLog,
    client: str | None = None,
) -> OrderNotificationLog:
    client = check_client_validation(client)

    db_log_record = save_log_record(
        log_record=log_record,
        client=client,
    )
    return db_log_record


def update_order_notification_log_record(
    log_record: OrderNotificationLog,
    client: str | None = None,
) -> OrderNotificationLog:
    client = check_client_validation(client)

    db_log_record = update_log_record(
        log_record=log_record,
        client=client,
    )
    return db_log_record
