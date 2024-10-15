from repository.emergency_class.emergency_classification_history_repository import save_history_record
from scheme.emergency_class.emergency_classification_history_scheme import EmergencyClassificationRecord


def save_emergency_classification_record(
    record: EmergencyClassificationRecord,
) -> EmergencyClassificationRecord:
    record_db = save_history_record(record)
    return record_db
