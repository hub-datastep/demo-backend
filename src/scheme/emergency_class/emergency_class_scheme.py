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


class SummaryValue(SQLModel):
    id: str | None
    value: str | None
    fileTypeId: int | None


class Summary(SQLModel):
    id: int | None
    type: str
    title: str
    name: str | None
    value: str
    target: str | None
    price: float | None
    currency: str | None
    elementValueId: int | None
    values: list[SummaryValue] | None
    elementValueIds: list[int] | None


class OrderDetails(SQLModel):
    id: int
    # List of order params
    summary: list[Summary]


class OrderData(SQLModel):
    # Resident order id
    orderId: int
    orderStatusId: int | None
    orderExtId: str | None
    rating: int | None
    unregisteredAddress: str | None
    unregisteredPhoneNumber: str | None
    unregisteredCustomerName: str | None


class EmergencyClassRequest(SQLModel):
    alertId: str
    alertTypeId: int
    timestamp: int | None
    data: OrderData


# class OrderUpdate(SQLModel):
#     isAccident: bool
#     orderStatusId: int


class EmergencyClassResponse(SQLModel):
    order_id: int
    order_query: str | None
    is_accident: bool
    order_emergency: str
    # Response from Domyland API
    order_update_response: dict | None
