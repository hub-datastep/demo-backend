from sqlalchemy import func
from sqlmodel import Session, and_, select

from infra.database import engine
from infra.domyland.constants import OrderStatusID
from middleware.error_handle_middleware import handle_errors
from repository.base import BaseRepository
from repository.order_classification.order_classification_history_repository import (
    create_schema_and_table,
)
from scheme.order_notification.order_notification_logs_scheme import (
    OrderNotificationLog,
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


def update_log_record(
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
        db_log_record = session.merge(log_record)
        session.commit()
        session.refresh(db_log_record)
        return db_log_record


class OrderNotificationLogRepository(BaseRepository[OrderNotificationLog]):
    def __init__(self) -> None:
        super().__init__(schema=OrderNotificationLog)

    @handle_errors
    async def get_by_order_id(
        self,
        order_id: int,
        client: str | None = None,
    ) -> OrderNotificationLog | None:
        async with self.get_session() as session:
            # Create schema and table if not exists
            self.create_schema_and_table(schema=client)

            # Set table schema
            OrderNotificationLog.__table__.schema = client

            st = select(self.schema)
            # Same order ID
            st = st.where(self.schema.order_id == order_id)
            # Status ID 1 (status "Ожидание")
            st = st.where(self.schema.order_status_id == OrderStatusID.PENDING)
            # Order resident query exists and not empty
            st = st.where(
                and_(
                    self.schema.order_query.is_not(None),
                    func.length(func.trim(self.schema.order_query)) > 0,
                )
            )
            # Our Comment exists
            st = st.where(self.schema.comment == None)
            # Without Errors
            st = st.where(self.schema.is_error == False)
            st = st.order_by(self.schema.created_at.desc(), self.schema.id.desc())

            result = await session.exec(st)

            return result.first()

    @handle_errors
    async def create(
        self,
        log_record: OrderNotificationLog,
        client: str | None = None,
    ) -> OrderNotificationLog:
        # Set schema to save record in specified history table
        log_record.__table__.schema = client

        async with self.get_session() as session:
            # Create schema and table if not exists
            self.create_schema_and_table(schema=client)

            # Save history record
            session.add(log_record)
            await session.commit()
            await session.refresh(log_record)
            return log_record


order_notification_log_repository = OrderNotificationLogRepository()
