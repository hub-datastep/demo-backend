from typing import Literal
from uuid import UUID

from sqlmodel import SQLModel, Field


class Nomenclature(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nomenclature: str
    group: str
    embeddings: str | None = None


class OneNomenclatureUpload(SQLModel):
    row_number: int
    nomenclature: str


class OneNomenclatureRead(SQLModel):
    row_number: int
    nomenclature: str
    status: Literal["progress", "finished", "queued", "error"]
    group: str | None
    mapping: str | None


class NomenclaturesUpload(SQLModel):
    nomenclatures: list[OneNomenclatureUpload]


class NomenclaturesRead(SQLModel):
    nomenclature_id: str
    ready_count: int
    total_count: int
    general_status: Literal["progress", "finished", "queued"]
    nomenclatures: list[OneNomenclatureRead]


class JobIdRead(SQLModel):
    nomenclature_id: str
