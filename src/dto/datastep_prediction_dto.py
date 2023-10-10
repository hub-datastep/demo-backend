from pydantic import BaseModel


class DatastepPredictionDto(BaseModel):
    answer: str
    sql: str | None
    table: str | None
    table_source: str | None


class DatastepPredictionOutDto(DatastepPredictionDto):
    similar_queries: list[str]
