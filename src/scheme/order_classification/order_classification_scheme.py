from sqlmodel import SQLModel

"""
Docs with type of Domyland.

https://public-api.domyland.ru/sud-api/webhooks/exploitation/
"""


class AlertTypeID:
    NEW_ORDER = 1
    UPDATE_ORDER_STATUS = 13


class OrderStatusID:
    PENDING = 1
    IN_PROGRESS = 2


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
    type: str | None = None
    title: str | None = None
    value: str | int | None = None


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
    typeId: int | None = None
    title: str
    value: int | str


class OrderFormUpdate(SQLModel):
    id: int
    value: int | str


class Service(SQLModel):
    orderForm: list[OrderForm]


class Resident(SQLModel):
    id: int
    firstName: str
    lastName: str
    middleName: str | None = None
    fullName: str | None = None
    image: str | None = None
    customerTypeId: int | None = None
    phoneNumber: str | None = None
    lastActivity: int | None = None
    sex: str | None = None
    customerStatus: str | None = None


class OrderDetails(SQLModel):
    order: Order
    # List of order params
    service: Service
    customer: Resident


class OrderData(SQLModel):
    # Resident order id
    orderId: int
    orderStatusId: int


class OrderClassificationRequest(SQLModel):
    alertId: str | None = None
    alertTypeId: int
    timestamp: int | None = None
    data: OrderData


class MostRelevantClassLLMResponse(SQLModel):
    order_class: str
    comment: str


class OrderClassificationLLMResponse(SQLModel):
    most_relevant_class_response: MostRelevantClassLLMResponse
    scores: str
    query_summary: str
