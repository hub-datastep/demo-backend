from infra.database import engine
from infra.domyland.constants import OrderStatusID
from scheme.order_notification.order_notification_logs_scheme import (
    OrderNotificationLog,
)
from sqlalchemy import func
from sqlmodel import and_, select, Session

from repository.order_classification.order_classification_history_repository import (
    create_schema_and_table,
)


def get_log_record_by_order_id(
    order_id: int,
    client: str | None = None,
) -> OrderNotificationLog | None:
    with Session(engine) as session:
        # Create schema and table if not exists
        create_schema_and_table(
            session=session,
            client=client,
        )

        # Set table schema
        OrderNotificationLog.__table__.schema = client

        st = select(OrderNotificationLog)
        # Same order ID
        st = st.where(OrderNotificationLog.order_id == order_id)
        # Status ID 1 (status "Ожидание")
        st = st.where(OrderNotificationLog.order_status_id == OrderStatusID.PENDING)
        # Order resident query exists and not empty
        st = st.where(
            and_(
                OrderNotificationLog.order_query.is_not(None),
                func.length(func.trim(OrderNotificationLog.order_query)) > 0,
            )
        )
        # Our Comment exists
        st = st.where(OrderNotificationLog.comment == None)
        # Without Errors
        st = st.where(OrderNotificationLog.is_error == False)

        result = session.exec(st).first()

        return result


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
