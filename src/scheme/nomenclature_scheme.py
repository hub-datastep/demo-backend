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
    group: str
    mapping: list[str]


class NomenclaturesUpload(SQLModel):
    nomenclatures: list[OneNomenclatureUpload]
    job_size: int


class NomenclaturesRead(SQLModel):
    nomenclature_id: str
    ready_count: int | None
    total_count: int | None
    general_status: str
    nomenclatures: list[OneNomenclatureRead]


class JobIdRead(SQLModel):
    nomenclature_id: str
