from datetime import datetime

from rq.job import JobStatus
from sqlmodel import SQLModel, Field


class ClassifierVersion(SQLModel, table=True):
    __tablename__ = "classifier_version"

    id: str = Field(primary_key=True)
    accuracy: float | None = Field(default=None)
    is_deleted: bool | None = Field(default=False)
    created_at: datetime | None = Field(default=datetime.utcnow())


class RetrainClassifierUpload(SQLModel):
    db_con_str: str
    table_name: str


class ClassifierVersionRead(SQLModel):
    model_id: str
    created_at: datetime


class ClassifierRetrainingResult(SQLModel):
    job_id: str
    status: JobStatus
    result: ClassifierVersionRead | None
