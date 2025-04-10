from model.base import BaseModel
from repository.order_notification.order_notification_logs_repository import (
    OrderNotificationLogRepository,
    order_notification_log_repository,
    save_log_record,
    update_log_record,
)
from scheme.order_notification.order_notification_logs_scheme import (
    OrderNotificationLog,
)
from util.client_db_schema import get_db_schema_by_client


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
    client = get_db_schema_by_client(client)

    db_log_record = save_log_record(
        log_record=log_record,
        client=client,
    )
    return db_log_record


def update_order_notification_log_record(
    log_record: OrderNotificationLog,
    client: str | None = None,
) -> OrderNotificationLog:
    client = get_db_schema_by_client(client)

    db_log_record = update_log_record(
        log_record=log_record,
        client=client,
    )
    return db_log_record


class OrderNotificationLogModel(
    BaseModel[
        OrderNotificationLog,
        OrderNotificationLogRepository,
    ]
):
    def __init__(self) -> None:
        super().__init__(
            schema=OrderNotificationLog,
            repository=order_notification_log_repository,
        )

    async def get_by_order_id(
        self,
        order_id: int,
        client: str | None = None,
    ) -> OrderNotificationLog | None:
        client = get_db_schema_by_client(client=client)

        saved_record = await self.repository.get_by_order_id(
            order_id=order_id,
            client=client,
        )
        return saved_record

    async def create(
        self,
        log_record: OrderNotificationLog,
        client: str | None = None,
    ) -> OrderNotificationLog:
        client = get_db_schema_by_client(client=client)

        db_log_record = await self.repository.create(
            log_record=log_record,
            client=client,
        )
        return db_log_record


order_notification_log_model = OrderNotificationLogModel()
