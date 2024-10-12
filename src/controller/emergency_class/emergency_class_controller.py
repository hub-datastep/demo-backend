from fastapi import APIRouter, status, Depends
from fastapi import Response
from fastapi_versioning import version
from sqlmodel import Session

from controller.user.user_controller import get_current_user
from infra.database import get_session
from model.emergency_class import emergency_class_model, emergency_classification_config_model
from scheme.emergency_class.emergency_class_scheme import EmergencyClassRequest
from scheme.emergency_class.emergency_classification_config_scheme import EmergencyClassificationConfig
from scheme.emergency_class.emergency_classification_history_scheme import EmergencyClassificationRecord
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("/config/{user_id}", response_model=EmergencyClassificationConfig)
@version(1)
def get_emergency_classification_config_by_user_id(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    """
    return emergency_classification_config_model.get_emergency_classification_config_by_user_id(
        session=session,
        user_id=user_id,
    )


@router.post("/", response_model=EmergencyClassificationRecord)
@version(1)
def get_emergency_class(
    body: EmergencyClassRequest,
    # current_user: UserRead = Depends(get_current_user),
    # Init response to return object and change status code if needed
    response: Response,
):
    """
    Вебхук для обновления аварийности заявки в Домиленд.
    """
    emergency_classification_response = emergency_class_model.get_emergency_class(body)

    response_status = status.HTTP_200_OK
    if emergency_classification_response.is_error:
        response_status = status.HTTP_500_INTERNAL_SERVER_ERROR

    response.status_code = response_status
    return emergency_classification_response
