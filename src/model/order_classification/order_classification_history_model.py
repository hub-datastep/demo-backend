from repository.order_classification.order_classification_history_repository import (
    get_history_record_by_order_id,
    save_history_record,
)
from scheme.order_classification.order_classification_history_scheme import (
    OrderClassificationRecord,
)


def get_saved_record_by_order_id(
    order_id: int,
    client: str,
) -> OrderClassificationRecord | None:
    saved_record = get_history_record_by_order_id(
        order_id=order_id,
        client=client,
    )
    return saved_record


def save_order_classification_record(
    record: OrderClassificationRecord,
    client: str,
) -> OrderClassificationRecord:
    record_db = save_history_record(
        record=record,
        client=client,
    )
    return record_db
