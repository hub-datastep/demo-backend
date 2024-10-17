from sqlmodel import SQLModel


class MappingOneNomenclatureUpload(SQLModel):
    row_number: int
    nomenclature: str


class MappingOneTargetRead(SQLModel):
    nomenclature_guid: str
    nomenclature: str
    group: str | None
    similarity_score: float


class MappingOneNomenclatureRead(SQLModel):
    row_number: int
    nomenclature: str
    group: str | None
    internal_group: str
    nomenclature_params: list[dict] | None
    mappings: list[MappingOneTargetRead] | None
    similar_mappings: list[MappingOneTargetRead] | None


class MappingNomenclaturesUpload(SQLModel):
    nomenclatures: list[MappingOneNomenclatureUpload]
    most_similar_count: int = 3
    chunk_size: int = 100


class MappingNomenclaturesResultRead(SQLModel):
    job_id: str
    ready_count: int | None
    total_count: int | None
    general_status: str
    nomenclatures: list[MappingOneNomenclatureRead] | None
