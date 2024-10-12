from fastapi import APIRouter, status
from fastapi import Response
from fastapi_versioning import version

from model.emergency_class import emergency_class_model
from scheme.emergency_class.emergency_class_scheme import EmergencyClassRequest
from scheme.emergency_class.emergency_classification_history_scheme import EmergencyClassificationRecord

router = APIRouter()


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
