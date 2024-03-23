from datetime import datetime
from typing import Literal

from sqlmodel import SQLModel, Field


class Nomenclature(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nomenclature: str
    group: str
    embeddings: str | None = None


class OneNomenclatureUpload(SQLModel):
    row_number: int
    nomenclature: str


class MappingRead(SQLModel):
    nomenclature_guid: str
    nomenclature: str
    similarity_score: float


class OneNomenclatureRead(SQLModel):
    row_number: int
    nomenclature: str | None
    group: str
    mappings: list[MappingRead]


class NomenclaturesUpload(SQLModel):
    nomenclatures: list[OneNomenclatureUpload]
    most_similar_count: int = 1
    job_size: int


class NomenclaturesRead(SQLModel):
    job_id: str
    ready_count: int | None
    total_count: int | None
    general_status: str
    nomenclatures: list[OneNomenclatureRead]


class JobIdRead(SQLModel):
    job_id: str


class CreateAndSaveEmbeddings(SQLModel):
    nom_db_con_str: str
    table_name: str
    top_n: int
    order_by: str
    offset: int
    chroma_collection_name: str


class SyncNomenclaturesUpload(SQLModel):
    nom_db_con_str: str
    chroma_collection_name: str
    sync_period: int


class SyncOneNomenclature(SQLModel):
    id: str
    nomenclature_name: str
    group: str


class SyncNomenclaturesPatch(SQLModel):
    nomenclature_data: SyncOneNomenclature
    action: Literal["delete", "update", "create"]


class MsuDatabaseOneNomenclatureRead(SQLModel, table=True):
    __tablename__ = "СправочникНоменклатура"
    __table_args__ = {"schema": "us"}

    id: str = Field(sa_column_kwargs={"name": "Ссылка"}, primary_key=True)
    nomenclature_name: str = Field(sa_column_kwargs={"name": "Наименование"})
    group: str = Field(sa_column_kwargs={"name": "Родитель"})
    is_group: bool = Field(sa_column_kwargs={"name": "ЭтоГруппа"})
    is_deleted: bool = Field(sa_column_kwargs={"name": "ПометкаУдаления"})
    edited_at: datetime = Field(sa_column_kwargs={"name": "МСУ_ДатаИзменения"})
    root_group_name: str | None = Field(sa_column_kwargs={"_omit_from_statements": True})
    is_in_vectorstore: bool | None = Field(sa_column_kwargs={"_omit_from_statements": True})


class SyncNomenclaturesRead(SQLModel):
    id: str
    nomenclature_name: str
    group: str
    action: Literal["delete", "update", "create"]
