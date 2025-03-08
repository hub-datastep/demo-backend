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


class OrderStatusDetails(SQLModel):
    responsibleDeptId: int | None = None
    responsibleUsers: list[OrderResponsibleUser] | None = []
    comment: str | None = ""
