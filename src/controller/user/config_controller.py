from dto.config_dto import DatabasePredictionConfigDto
from fastapi import APIRouter, Depends
from fastapi_versioning import version

from model.auth_model import get_current_user
from repository import config_repository
from scheme.user_scheme import UserRead

router = APIRouter()


@router.get("/database_prediction", response_model=DatabasePredictionConfigDto | None)
@version(1)
def get_database_prediction_config(
    *,
    current_user: UserRead = Depends(get_current_user)
):
    """
    """
    return config_repository.get_database_prediction_config(current_user.id)


@router.put("/database_prediction", response_model=DatabasePredictionConfigDto)
@version(1)
def update_database_prediction_config(
    *,
    current_user: UserRead = Depends(get_current_user),
    update: DatabasePredictionConfigDto
):
    """
    """
    return config_repository.update_database_prediction_config(current_user.id, update)
