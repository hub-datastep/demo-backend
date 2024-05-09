from datetime import datetime
from typing import Literal

from rq.job import JobStatus
from sqlmodel import SQLModel, Field


class MappingOneNomenclatureUpload(SQLModel):
    row_number: int
    nomenclature: str


class MappingOneTargetRead(SQLModel):
    nomenclature_guid: str
    nomenclature: str
    similarity_score: float


class MappingOneNomenclatureRead(SQLModel):
    row_number: int
    nomenclature: str | None
    group: str
    mappings: list[MappingOneTargetRead] | None


class MappingNomenclaturesUpload(SQLModel):
    nomenclatures: list[MappingOneNomenclatureUpload]
    most_similar_count: int = 1
    job_size: int
    chroma_collection_name: str


class MappingNomenclaturesResultRead(SQLModel):
    job_id: str
    ready_count: int | None
    total_count: int | None
    general_status: str
    nomenclatures: list[MappingOneNomenclatureRead]


class CreateAndSaveEmbeddingsUpload(SQLModel):
    nom_db_con_str: str
    table_name: str
    top_n: int
    order_by: str
    offset: int
    chroma_collection_name: str


class SyncOneNomenclatureDataRead(SQLModel):
    id: str
    nomenclature_name: str
    group: str


SyncOneNomenclatureAction = Literal["delete", "update", "create"]


class SyncNomenclaturesUpload(SQLModel):
    nom_db_con_str: str
    chroma_collection_name: str
    sync_period: int


class SyncNomenclaturesChromaPatch(SQLModel):
    nomenclature_data: SyncOneNomenclatureDataRead
    action: SyncOneNomenclatureAction


class SyncNomenclaturesResultRead(SQLModel):
    job_id: str
    status: JobStatus
    updated_nomenclatures: list[SyncNomenclaturesChromaPatch] | None
    ready_count: int | None
    total_count: int | None


class MsuDatabaseOneNomenclatureRead(SQLModel, table=True):
    __tablename__ = "СправочникНоменклатура"
    __table_args__ = {
        "schema": "us"
    }

    id: str = Field(sa_column_kwargs={"name": "Ссылка"}, primary_key=True, max_length=255)
    nomenclature_name: str = Field(sa_column_kwargs={"name": "Наименование"})
    group: str = Field(sa_column_kwargs={"name": "Родитель"})
    is_group: int = Field(sa_column_kwargs={"name": "ЭтоГруппа"})
    is_deleted: int = Field(sa_column_kwargs={"name": "ПометкаУдаления"})
    edited_at: datetime = Field(sa_column_kwargs={"name": "МСУ_ДатаИзменения"})
    root_group_name: str | None = Field(sa_column_kwargs={"_omit_from_statements": True})
    is_in_vectorstore: bool | None = Field(sa_column_kwargs={"_omit_from_statements": True})


class JobIdRead(SQLModel):
    job_id: str


class SyncNomenclaturesByViewsUpload(SQLModel):
    db_con_str: str
    table_name: str
    chroma_collection_name: str
