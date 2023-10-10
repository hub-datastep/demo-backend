from pydantic import BaseModel


class DatastepPredictionDto(BaseModel):
    page: int | None = None
    answer: str
    sql: str | None
    table: str | None
    table_source: str | None = None


class DatastepPredictionOutDto(DatastepPredictionDto):
    similar_queries: list[str]
