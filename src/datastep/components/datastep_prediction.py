from pydantic import BaseModel


class DatastepPrediction(BaseModel):
    answer: str
    sql: str
    table: str


class DatastepPredictionDto(BaseModel):
    answer: str
    sql: str | None
    table: str | None
    is_exception: bool
