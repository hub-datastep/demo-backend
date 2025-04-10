from sqlmodel import SQLModel

from scheme.order_classification.order_classification_scheme import OrderResponsibleUser


class NotificationData(SQLModel):
    orderId: int
    orderStatusId: int


class OrderNotificationRequestBody(SQLModel):
    alertId: str | None = None
    alertTypeId: int
    timestamp: int | None = None
    data: NotificationData
    crm: str | None = None
    client: str | None = None


class OrderStatusDetails(SQLModel):
    responsibleDeptId: int | None = None
    responsibleUsers: list[OrderResponsibleUser] | None = []
    comment: str | None = ""


class CleaningResultMessageLLMResponse(SQLModel):
    # Коммент исполнителя после фильтрации
    filtered_comment: str | None = None
    # Пояснение LLM как она писала сообщение
    comment: str | None = None
    # Текст сообщения
    message: str | None = None
