from sqlmodel import SQLModel


class PredictionQueryBase(SQLModel):
    query: str


class DatabasePredictionQuery(PredictionQueryBase):
    tables: list[str]
    limit: int = 10


class DocumentPredictionQuery(PredictionQueryBase):
    file_id: int


class PredictionReadBase(SQLModel):
    answer: str


class DatabasePredictionRead(PredictionReadBase):
    sql: str
    table: str
    table_source: str
    similar_queries: list[str]


class DocumentPredictionRead(PredictionReadBase):
    page: int


class KnowledgeBasePredictionRead(PredictionReadBase):
    file_path: str | None = None
    filename: str | None = None
