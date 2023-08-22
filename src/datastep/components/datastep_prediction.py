from pydantic import BaseModel


class DatastepPrediction(BaseModel):
    answer: str
    sql: str
    table: str


class DatastepPredictionDto(BaseModel):
    answer: str
    sql: str | None = None
    table: str | None = None
