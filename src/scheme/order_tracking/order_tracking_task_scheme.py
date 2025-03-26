from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from infra.order_tracking.action import OrderTrackingTaskAction
from infra.order_tracking.task_status import OrderTrackingTaskStatus
from scheme.order_classification.order_classification_config_scheme import (
    OrderClassificationConfig,
)


class OrderTrackingTaskBase(SQLModel):
    # ID конфига
    config_id: int = Field(foreign_key="order_classification_config.id")
    # ID заявки, которую трекаем
    order_id: int
    # Данные заявки, которые получали последний раз
    last_order_details: dict | None = Field(default=None, sa_column=Column(JSONB))
    # Внутренний статус задачи
    internal_status: str | None = Field(default=OrderTrackingTaskStatus.PENDING)
    # Экшен, который нужно сделать
    next_action: str | None = Field(default=OrderTrackingTaskAction.FETCH_ORDER_DETAILS)
    # Логи предыдущих экшенов
    actions_logs: list[dict] | None = Field(default=None, sa_column=Column(JSONB))
    # Дата и время, когда нужно сделать экшен
    action_time: datetime | None = None
    # Закончили ли задачу
    is_completed: bool | None = None
    # Дата и время, когда создали задачу
    created_at: datetime | None = None
    # Дата и время, когда закончили задачу
    finished_at: datetime | None = None


class OrderTrackingTask(OrderTrackingTaskBase, table=True):
    __tablename__ = "order_tracking_task"

    id: int | None = Field(default=None, primary_key=True)

    config: OrderClassificationConfig = Relationship()


class OrderTrackingTaskActinLog(SQLModel):
    """
    Logs that saved in `actions_logs` in `OrderTrackingTask`
    """

    # Была ли ошибка при выполнении
    is_error: bool | None = False
    # Название экшена
    name: str | None = None
    # Дата и время начала выполнения
    started_at: datetime | None = None
    # Дата и время конца выполнения
    finished_at: datetime | None = None
    # Дополнительная информация
    metadatas: dict | None = None
