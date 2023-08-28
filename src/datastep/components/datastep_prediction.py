from pydantic import BaseModel


class DatastepPrediction(BaseModel):
    answer: str
    sql: str | None
    table: str | None
    is_exception: bool


class DatastepPredictionDto(BaseModel):
    answer: str
    sql: str | None
    table: str | None
