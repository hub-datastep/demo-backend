from model.order_classification import order_get_info
from fastapi import APIRouter, status
from fastapi_versioning import version
from fastapi.requests import Request

router = APIRouter()


@router.post("/order_updated")
@router.post("/new_order_comment")
@router.post("/SLA_order_exec_time_violated")
@router.post("/order_deadline_coming")
@router.post("/order_new_message")
@router.post("/order_status_updated")
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
