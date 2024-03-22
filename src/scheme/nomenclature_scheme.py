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
    table_name: str
    chroma_collection_name: str
    sync_period: int


class SyncOneNomenclatureCreateOrUpdate(SQLModel):
    id: str
    nomenclature_name: str | None
    group: str | None


class SyncOneNomenclatureDelete(SQLModel):
    id: str


class SyncNomenclaturesPatch(SQLModel):
    nomenclature_data: SyncOneNomenclatureCreateOrUpdate | SyncOneNomenclatureDelete
    action: Literal["delete", "update", "create"]

