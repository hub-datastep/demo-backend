from repository.order_notification.order_notification_logs_repository import (
    get_log_record_by_order_id,
    save_log_record,
)
from scheme.order_notification.order_notification_logs_scheme import (
    OrderNotificationLog,
)

from model.order_classification.order_classification_history_model import (
    check_client_validation,
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


def save_order_notification_log_record(
    log_record: OrderNotificationLog,
    client: str | None = None,
) -> OrderNotificationLog:
    client = check_client_validation(client)

    log_record_db = save_log_record(
        log_record=log_record,
        client=client,
    )
    return log_record_db
