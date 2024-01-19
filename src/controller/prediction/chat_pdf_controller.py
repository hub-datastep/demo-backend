from fastapi import APIRouter
from fastapi_versioning import version

from dto.datastep_prediction_dto import DatastepPredictionOutDto
from dto.query_dto import QueryDto
from model import datastep_pdf_model

# from service.auth_service import AuthService

router = APIRouter()


@router.post("/prediction", response_model=DatastepPredictionOutDto)
@version(1)
def get_prediction(
    body: QueryDto,
    # current_user: UserDto = Depends(AuthService.get_current_user)
):
    return datastep_pdf_model.get_prediction(body.filename, body.query)
