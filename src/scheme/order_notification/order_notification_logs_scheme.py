from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class OrderNotificationLogBase(SQLModel):
    is_error: bool = False
    # Webhook Request Body
    input_request_body: dict | None = Field(default=None, sa_column=Column(JSONB))
    # Order Data
    order_id: int
    order_status_id: int
    order_query: str | None = None
    order_status_comment: str | None = None
    order_details: dict | None = Field(default=None, sa_column=Column(JSONB))
    # Some other Data
    actions_logs: list[dict] | None = Field(default=None, sa_column=Column(JSONB))
    # LLM Response
    message_llm_response: dict | None = Field(default=None, sa_column=Column(JSONB))
    # Just for errors messages or our comments
    comment: str | None = None


class OrderNotificationLog(OrderNotificationLogBase, table=True):
    __tablename__ = "order_notification_logs"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
