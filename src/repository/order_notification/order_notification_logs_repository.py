from infra.database import engine
from scheme.order_notification.order_notification_logs_scheme import (
    OrderNotificationLog,
)
from sqlmodel import Session

from repository.order_classification.order_classification_history_repository import (
    create_schema_and_table,
)


def save_log_record(
    log_record: OrderNotificationLog,
    client: str | None = None,
) -> OrderNotificationLog:
    # Set schema to save record in specified history table
    log_record.__table__.schema = client

    with Session(engine) as session:
        # Create schema and table if not exists
        create_schema_and_table(
            session=session,
            client=client,
        )

        # Save history record
        session.add(log_record)
        session.commit()
        session.refresh(log_record)
        return log_record
