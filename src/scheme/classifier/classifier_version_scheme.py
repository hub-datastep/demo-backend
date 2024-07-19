from datetime import datetime

from rq.job import JobStatus
from sqlmodel import SQLModel, Field


class ClassifierVersion(SQLModel, table=True):
    __tablename__ = "classifier_version"

    id: str = Field(primary_key=True)
    description: str | None = Field()
    accuracy: float | None = Field(default=None)
    is_deleted: bool | None = Field(default=False)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)


class RetrainClassifierUpload(SQLModel):
    db_con_str: str
    table_name: str
    model_description: str
    use_params: bool = True


class ClassifierVersionRead(SQLModel):
    model_id: str
    description: str
    created_at: datetime


class ClassifierRetrainingResult(SQLModel):
    job_id: str
    status: JobStatus
    retrain_status: str | None
    result: ClassifierVersionRead | None


class ClassificationResultItem(SQLModel):
    item: str
    group: str


class ClassificationResult(SQLModel):
    job_id: str
    status: JobStatus
    result: list[ClassificationResultItem] | None
