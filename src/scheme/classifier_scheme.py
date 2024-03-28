from datetime import datetime
from typing import Literal

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


SyncOneClassifierVersionAction = Literal["delete"]


class SyncClassifierVersionPatch(SQLModel):
    model_id: str
    action: SyncOneClassifierVersionAction


class ClassifierRetrainingResult(SQLModel):
    job_id: str
    status: JobStatus
    result: ClassifierVersionRead | None
    changes: list[SyncClassifierVersionPatch] | None
