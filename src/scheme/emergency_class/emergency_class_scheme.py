from enum import Enum

from sqlmodel import SQLModel

"""
Docs with type of Domyland.

https://public-api.domyland.ru/sud-api/webhooks/exploitation/
"""


class SummaryType(str, Enum):
    STRING = "string"
    RADIO = "radio"
    TEXT = "text"
    IMAGE = "image"


class SummaryTitle(str, Enum):
    ADDRESS = "Адрес"
    OBJECT = "Объект"
    ISSUE = "Что случилось?"
    COMMENT = "Комментарий"
    ATTACH_PHOTO = "Прикрепите фото"


class SummaryValue(SQLModel):
    id: str | None
    value: str | None
    fileTypeId: int | None


class Summary(SQLModel):
    id: int | None
    type: SummaryType
    title: SummaryTitle
    name: str | None
    value: str
    target: str | None
    price: float | None
    currency: str | None
    elementValueId: int | None
    values: list[SummaryValue] | None
    elementValueIds: list[int] | None


class OrderData(SQLModel):
    title: str | None
    # Resident order id
    orderId: int
    serviceId: int | None
    orderExtId: str | None
    rating: int | None
    ratingComment: str | None
    orderStatusId: int | None
    unregisteredAddress: str | None
    unregisteredPhoneNumber: str | None
    unregisteredCustomerName: str | None
    # List with order details
    summary: list[Summary]


class EmergencyClassRequest(SQLModel):
    alertId: str
    alertTypeId: int
    timestamp: int | None
    data: OrderData
