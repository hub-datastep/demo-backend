from fastapi import APIRouter
from fastapi_versioning import version

from datastep.components.datastep_prediction import DatastepPredictionDto
from dto.query_dto import QueryDto
from model import datastep_model

router = APIRouter(
    prefix="/assistant",
    tags=["assistant"],
)


@router.post("/prediction", response_model=DatastepPredictionDto)
@version(1)
async def get_prediction(body: QueryDto):
    return datastep_model.get_prediction(body)


@router.get("/reset_context")
@version(1)
async def reset_context() -> None:
    return datastep_model.reset()
