from fastapi import APIRouter, status
from fastapi.requests import Request
from fastapi_versioning import version

from infra.env import env
from infra.kafka.brokers import kafka_broker
from infra.kafka.helpers import send_message_to_kafka
from middleware.kafka_middleware import with_kafka_broker_connection
from model.order_classification import order_get_info
from scheme.order_notification.order_notification_scheme import (
    OrderNotificationRequestBody,
)

router = APIRouter()


@router.post("/order_updated")
@router.post("/new_order_comment")
@router.post("/SLA_order_exec_time_violated")
@router.post("/order_deadline_coming")
@router.post("/order_new_message")
@version(1)
def order_notifications(
    body: dict,
    request: Request,
    crm: str | None = None,
    client: str | None = None,
):
    """
    Вебхук об обновления заявки в Домиленде.
    """

    url = str(request.url)
    order_get_info.get_order_details(body=body, url=url)
    return status.HTTP_200_OK


@router.post("/order_status_updated")
@version(1)
@with_kafka_broker_connection(kafka_broker)
async def process_order_status_updated_event(
    body: OrderNotificationRequestBody,
    crm: str | None = None,
    client: str | None = None,
):
    """
    Вебхук для ивента "Статус Заявки Обновлён" в Домиленд.
    Переотправляет запрос в Кафку для последующей обработки ивента.
    """

    body.crm = crm
    body.client = client
    order_id = body.data.orderId

    await send_message_to_kafka(
        broker=kafka_broker,
        message_body=body,
        topic=env.KAFKA_ORDER_NOTIFICATIONS_TOPIC,
        key=str(order_id),
    )
