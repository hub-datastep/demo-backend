from fastapi import APIRouter, status, Depends
from fastapi import Response
from fastapi_versioning import version
from sqlmodel import Session

from controller.user.user_controller import get_current_user
from infra.database import get_session
from model.order_classification import order_classification_model, order_classification_config_model, order_get_info
from scheme.order_classification.order_classification_config_scheme import OrderClassificationConfig
from scheme.order_classification.order_classification_history_scheme import OrderClassificationRecord
from scheme.order_classification.order_classification_scheme import OrderClassificationRequest
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("/config/id/{config_id}", response_model=OrderClassificationConfig)
@version(1)
def get_classification_config_by_id(
    config_id: int,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    """
    return order_classification_config_model.get_order_classification_config_by_id(
        session=session,
        config_id=config_id,
    )


@router.get("/config/user_id/{user_id}", response_model=OrderClassificationConfig)
@version(1)
def get_classification_config_by_user_id(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    """
    return order_classification_config_model.get_order_classification_config_by_user_id(
        session=session,
        user_id=user_id,
    )


@router.post("/new_order", response_model=OrderClassificationRecord)
@version(1)
def classify_order(
    body: OrderClassificationRequest,
    # Init response to return object and change status code if needed
    response: Response,
    crm: str | None = None,
    client: str | None = None,
):
    """
    Вебхук для обновления аварийности заявки в Домиленд.
    """
    order_classification_response = order_classification_model.classify_order(
        body=body,
        client=client,
    )

    response_status = status.HTTP_200_OK
    if order_classification_response.is_error:
        response_status = status.HTTP_400_BAD_REQUEST

    response.status_code = response_status
    return order_classification_response

@router.post("/order_updated")
@router.post("/new_order_comment")
@router.post("/SLA_order_exec_time_violated")
@router.post("/order_deadline_coming")
@version(1)
def WebhookLog(
    body: OrderClassificationRequest,
    response: Response,
    crm: str | None = None,
    client: str | None = None,
):
    """
    Вебхук об обновления заявки в Домиленде.
    """
    

    order_get_info.get_order_details(body)
    return status.HTTP_200_OK