from pydantic import BaseModel


class DatastepPrediction(BaseModel):
    answer: str
    sql: str
    table: str
