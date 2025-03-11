from repository.order_notification.order_notification_logs_repository import (
    save_log_record,
)
from scheme.order_notification.order_notification_logs_scheme import (
    OrderNotificationLog,
)

from model.order_classification.order_classification_history_model import (
    check_client_validation,
)


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
