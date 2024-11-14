from repository.order_classification.order_classification_history_repository import save_history_record
from scheme.order_classification.order_classification_history_scheme import OrderClassificationRecord


def save_emergency_classification_record(
    record: OrderClassificationRecord,
    client: str,
) -> OrderClassificationRecord:
    record_db = save_history_record(
        record=record,
        client=client
    )
    return record_db
