from fastapi import APIRouter, status, Depends
from fastapi import Response
from fastapi_versioning import version
from sqlmodel import Session

from controller.user.user_controller import get_current_user
from infra.database import get_session
from model.order_classification import order_classification_model, order_classification_config_model
from scheme.order_classification.order_classification_config_scheme import OrderClassificationConfig
from scheme.order_classification.order_classification_history_scheme import OrderClassificationRecord
from scheme.order_classification.order_classification_scheme import OrderClassificationRequest
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("/config/{user_id}", response_model=OrderClassificationConfig)
@version(1)
def get_classification_config_by_user_id(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    """
    return order_classification_config_model.get_emergency_classification_config_by_user_id(
        session=session,
        user_id=user_id,
    )


@router.post("/new_order", response_model=OrderClassificationRecord)
@version(1)
def get_emergency_class(
    client: str,
    crm: str,
    body: OrderClassificationRequest,
    # Init response to return object and change status code if needed
    response: Response,
):
    """
    Вебхук для обновления аварийности заявки в Домиленд.
    """
    emergency_classification_response = order_classification_model.get_emergency_class(
        body=body,
        client=client,
    )

    response_status = status.HTTP_200_OK
    if emergency_classification_response.is_error:
        response_status = status.HTTP_500_INTERNAL_SERVER_ERROR

    response.status_code = response_status
    return emergency_classification_response
