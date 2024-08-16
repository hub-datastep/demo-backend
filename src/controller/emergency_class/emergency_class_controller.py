from fastapi import APIRouter
from fastapi import Depends
from fastapi_versioning import version

from model.auth.auth_model import get_current_user
from model.emergency_class import emergency_class_model
from scheme.emergency_class.emergency_class_scheme import EmergencyClassRequest
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.put("/")
@version(1)
def get_emergency_class(
    body: EmergencyClassRequest,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Вебхук для обновления аварийности заявки в Домиленд.
    """
    return emergency_class_model.get_emergency_class(body=body)
