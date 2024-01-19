from fastapi import APIRouter
from fastapi_versioning import version

from dto.config_dto import DatabasePredictionConfigDto
from repository import config_repository

# from service.auth_service import AuthService

router = APIRouter()


@router.get("/database_prediction", response_model=DatabasePredictionConfigDto | None)
@version(1)
def get_database_prediction_config(
    # current_user: UserDto = Depends(AuthService.get_current_user),
):
    return config_repository.get_database_prediction_config(current_user.id)


@router.put("/database_prediction", response_model=DatabasePredictionConfigDto)
@version(1)
def update_database_prediction_config(
    update: DatabasePredictionConfigDto,
    # current_user: UserDto = Depends(AuthService.get_current_user)
):
    return config_repository.update_database_prediction_config(current_user.id, update)
