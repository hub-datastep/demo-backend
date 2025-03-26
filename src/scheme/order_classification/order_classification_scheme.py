from sqlmodel import SQLModel

"""
Docs with type of Domyland.

https://public-api.domyland.ru/sud-api/webhooks/exploitation/
"""


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
    COMMENT = "Комментар"
    ATTACH_PHOTO = "Прикрепите фото"
    WHAT_REASON = "С чем связано обращение?"
    JOB_TYPE = "Выберите вид работ"


class OrderSummary(SQLModel):
    type: str | None = None
    title: str | None = None
    value: str | int | float | list | None = None


class OrderFile(SQLModel):
    id: int
    fileTypeId: int | None = None
    name: str | None = ""
    originalName: str | None = ""
    mime: str | None = ""
    url: str | None = ""
    isRemovable: int | None = None


class OrderResponsibleUser(SQLModel):
    id: int
    fullName: str | None = ""
    lastName: str | None = None
    firstName: str | None = None


class OrderStatusHistory(SQLModel):
    responsibleDeptId: int | None = None
    orderStatusId: int | None = None
    responsibleUsers: list[OrderResponsibleUser] | None = []


class OrderChatMessage(SQLModel):
    text: str | None = ""


class OrderChat(SQLModel):
    items: list[OrderChatMessage] | None = []


class Order(SQLModel):
    id: int
    serviceId: int
    eventId: int
    buildingId: int
    customerId: int
    placeId: int
    # Chat with Resident
    chat: OrderChat | None = None
    # Order Params from Resident
    summary: list[OrderSummary]
    # Files pinned to order from Responsible Users
    files: list[OrderFile] | None = []
    # Status Updates History
    statusHistory: list[OrderStatusHistory] | None = []
    # Current Responsible Users
    responsibleUsers: list[OrderResponsibleUser] | None = []
    # Current Status ID
    orderStatusId: int | None = None
    # Current Status Comment
    orderStatusComment: str | None = ""
    # Timestamp of SLA solve time
    solveTimeSLA: int | None = None


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
    # customer: Resident


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


class MessageFileToSend(SQLModel):
    fileName: str
