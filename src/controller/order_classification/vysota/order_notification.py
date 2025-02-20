from model.order_classification import order_get_info
from fastapi import APIRouter, status
from fastapi import Response
from fastapi_versioning import version

router = APIRouter()

@router.post("/order_updated")
@router.post("/new_order_comment")
@router.post("/SLA_order_exec_time_violated")
@router.post("/order_deadline_coming")
@router.post("/order_new_message")
@version(1)
def WebhookLog(
    body: dict,
    response: Response,
    crm: str | None = None,
    client: str | None = None,
):
    """
    Вебхук об обновления заявки в Домиленде.
    """
    

    order_get_info.get_order_details(body)
    return status.HTTP_200_OK