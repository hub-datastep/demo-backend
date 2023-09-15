from fastapi import APIRouter, Depends
from fastapi_versioning import version

from datastep.components.datastep_prediction import DatastepPredictionDto
from dto.query_dto import QueryDto
from dto.user_dto import UserDto
from model import datastep_model
from service.auth_service import AuthService

router = APIRouter(
    prefix="/assistant",
    tags=["assistant"],
)


@router.post("/prediction", response_model=DatastepPredictionDto)
@version(1)
async def get_prediction_v1(body: QueryDto, current_user: UserDto = Depends(AuthService.get_current_user)):
    return datastep_model.get_prediction_v1(body)


@router.post("/prediction", response_model=DatastepPredictionDto)
@version(2)
async def get_prediction_v2(body: QueryDto, current_user: UserDto = Depends(AuthService.get_current_user)):
    return datastep_model.get_prediction_v2(body)
