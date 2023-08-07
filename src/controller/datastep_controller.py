from fastapi import APIRouter

from datastep.components.datastep_prediction import DatastepPrediction
from dto.query_dto import QueryDto
from model import datastep_model

router = APIRouter(
    prefix="/datastep",
    tags=["datastep"],
)


@router.post("/prediction")
def get_prediction(body: QueryDto) -> DatastepPrediction:
    return datastep_model.get_prediction(body)
