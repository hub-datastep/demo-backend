from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.datastep_prediction_dto import DatastepPredictionOutDto
from dto.query_dto import QueryDto
from model import datastep_pdf_model
from model.auth_model import get_current_user
from scheme.user_scheme import UserRead

router = APIRouter()


@router.post("/prediction", response_model=DatastepPredictionOutDto)
@version(1)
def get_prediction(
    *,
    current_user: UserRead = Depends(get_current_user),
    body: QueryDto
    # current_user: UserDto = Depends(AuthService.get_current_user)
):
    return datastep_pdf_model.get_prediction(body.filename, body.query)
