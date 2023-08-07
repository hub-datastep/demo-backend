from datastep.components.datastep_prediction import DatastepPrediction
from dto.query_dto import QueryDto
from service.datastep_service import datastep_service


def get_prediction(body: QueryDto) -> DatastepPrediction:
    return datastep_service.run(body.query)
