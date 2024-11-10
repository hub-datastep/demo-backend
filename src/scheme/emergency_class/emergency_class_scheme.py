from sqlmodel import SQLModel

"""
Docs with type of Domyland.

https://public-api.domyland.ru/sud-api/webhooks/exploitation/
"""


class AlertTypeID:
    NEW_ORDER = 1
    UPDATE_ORDER_STATUS = 13


class SummaryType:
    STRING = "string"
    RADIO = "radio"
    TEXT = "text"
    IMAGE = "image"
    SELECT = "select"


class SummaryTitle:
    ADDRESS = "Адрес"
    OBJECT = "Объект"
    ISSUE = "Что случилось?"
    COMMENT = "Комментарий"
    ATTACH_PHOTO = "Прикрепите фото"
    WHAT_REASON = "С чем связано обращение?"
    JOB_TYPE = "Выберите вид работ"


class OrderSummary(SQLModel):
    type: str | None
    title: str | None
    value: str | None


class Order(SQLModel):
    id: int
    serviceId: int
    eventId: int
    buildingId: int
    customerId: int
    placeId: int
    summary: list[OrderSummary]


class OrderForm(SQLModel):
    id: int
    type: str
    typeId: int | None
    title: str
    value: int | str


class OrderFormUpdate(SQLModel):
    id: int
    value: int | str


class Service(SQLModel):
    orderForm: list[OrderForm]


class OrderDetails(SQLModel):
    order: Order
    # List of order params
    service: Service


class OrderData(SQLModel):
    # Resident order id
    orderId: int
    orderStatusId: int


class EmergencyClassRequest(SQLModel):
    alertId: str | None
    alertTypeId: int
    timestamp: int | None
    data: OrderData

# class OrderUpdate(SQLModel):
#     isAccident: bool
#     orderStatusId: int
