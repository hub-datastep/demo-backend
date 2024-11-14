from sqlalchemy.sql.ddl import CreateSchema
from sqlmodel import Session

from infra.database import engine
from scheme.order_classification.order_classification_history_scheme import OrderClassificationRecord


def save_history_record(
    record: OrderClassificationRecord,
    client: str,
) -> OrderClassificationRecord:
    # Set schema to save record in specified history table
    record.__table__.schema = client

    with Session(engine) as session:
        # Create schema for history table if not exists
        session.exec(
            CreateSchema(
                name=client,
                if_not_exists=True,
            )
        )
        session.commit()

        # Create table if not exists
        record.metadata.create_all(engine)

        # Save history record
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
