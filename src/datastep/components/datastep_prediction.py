from pydantic import BaseModel


class DatastepPrediction(BaseModel):
    answer: str
    sql: str | None
    table: str | None
    table_source: str | None
    is_exception: bool


class DatastepPredictionDto(BaseModel):
    answer: str
    sql: str | None
    table: str | None
    table_source: str | None
