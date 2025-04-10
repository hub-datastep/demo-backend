from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field


class OrderClassificationRecordBase(SQLModel):
    is_error: bool = False
    # Webhook alert data
    alert_id: str | None = None
    alert_type_id: int
    alert_timestamp: int | None = None
    # Order data
    order_id: int
    order_status_id: int
    order_query: str | None = None
    order_normalized_query: str | None = None
    order_details: dict | None = Field(default=None, sa_column=Column(JSONB))
    # LLM response
    order_class: str | None = None
    # UDS mapping data
    order_address: str | None = None
    responsible_user_id: str | None = None
    # Response from Domyland API
    order_update_request: dict | None = Field(default=None, sa_column=Column(JSONB))
    order_update_response: dict | None = Field(default=None, sa_column=Column(JSONB))
    # Just for errors messages or our comments
    comment: str | None = None
    llm_response: dict | None = Field(default=None, sa_column=Column(JSONB))


class OrderClassificationRecord(OrderClassificationRecordBase, table=True):
    __tablename__ = "order_classification_history"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
