from sqlmodel import Session

from infra.database import engine
from scheme.emergency_class.emergency_classification_history_scheme import EmergencyClassificationRecord


def save_history_record(
    record: EmergencyClassificationRecord,
) -> EmergencyClassificationRecord:
    with Session(engine) as session:
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
