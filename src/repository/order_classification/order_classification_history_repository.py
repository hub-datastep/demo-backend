from sqlalchemy import func
from sqlalchemy.sql.ddl import CreateSchema
from sqlmodel import Session, and_, select

from infra.database import engine
from scheme.order_classification.order_classification_history_scheme import (
    OrderClassificationRecord,
)
from scheme.order_classification.order_classification_scheme import OrderStatusID


def _create_schema_and_table(
    session: Session,
    client: str,
):
    # Set table schema
    OrderClassificationRecord.__table__.schema = client

    # Create schema for history table if not exists
    session.exec(
        CreateSchema(
            name=client,
            if_not_exists=True,
        )
    )
    session.commit()

    # Create table if not exists
    OrderClassificationRecord.metadata.create_all(engine)


def get_history_record_by_order_id(
    order_id: int,
    client: str,
) -> OrderClassificationRecord | None:
    with Session(engine) as session:
        # Create schema and table if not exists
        _create_schema_and_table(
            session=session,
            client=client,
        )

        # Set table schema
        OrderClassificationRecord.__table__.schema = client

        st = select(OrderClassificationRecord)
        # Same order ID
        st = st.where(OrderClassificationRecord.order_id == order_id)
        # Status ID 1 (status "Ожидание")
        st = st.where(
            OrderClassificationRecord.order_status_id == OrderStatusID.PENDING
        )
        # Order resident query is exists and not empty
        st = st.where(
            and_(
                OrderClassificationRecord.order_query.is_not(None),
                func.length(func.trim(OrderClassificationRecord.order_query)) > 0,
            )
        )
        # Order emergency is fully exists
        st = st.where(OrderClassificationRecord.order_emergency.is_not(None))
        st = st.where(OrderClassificationRecord.is_emergency.is_not(None))

        result = session.exec(st).first()

        return result


def save_history_record(
    record: OrderClassificationRecord,
    client: str,
) -> OrderClassificationRecord:
    # Set schema to save record in specified history table
    record.__table__.schema = client

    with Session(engine) as session:
        # Create schema and table if not exists
        _create_schema_and_table(
            session=session,
            client=client,
        )

        # Save history record
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
