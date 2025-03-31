from fastapi import APIRouter, Response, status
from fastapi.requests import Request
from fastapi_versioning import version
from loguru import logger

from model.order_classification import order_get_info
from model.order_notification import order_notification_model
from scheme.order_notification.order_notification_logs_scheme import (
    OrderNotificationLog,
)
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


@router.post("/order_status_updated", response_model=OrderNotificationLog)
@version(1)
def classify_order(
    body: OrderNotificationRequestBody,
    # Init response to return object and change status code if needed
    response: Response,
    crm: str | None = None,
    client: str | None = None,
):
    """
    Вебхук для ивента "Статус Заявки Обновлён" в Домиленд.
    """

    # Раскомментить когда починится баг когда мы ставим заявку в "выполнено" без отписки
    # logger.debug(f"OrderStatus Updated request body:\n{body}")

    # Раскомментить когда починится баг когда мы ставим заявку в "выполнено" без отписки
    # model_response = order_notification_model.process_event(
    #     body=body,
    #     client=client,
    # )

    # Раскомментить когда починится баг когда мы ставим заявку в "выполнено" без отписки
    # response_status = status.HTTP_200_OK
    # if model_response.is_error:
    #     response_status = status.HTTP_400_BAD_REQUEST
    # response.status_code = response_status

    # Удалить когда починится баг когда мы ставим заявку в "выполнено" без отписки
    logger.debug("Логика обработки ивента 'order_status_updated' временно закоменчена, чтобы не ставить клининг заявки в 'выполнено'")

    model_response = {}
    response.status_code = status.HTTP_200_OK

    return model_response
