from sqlmodel import SQLModel


class MappingOneNomenclatureUpload(SQLModel):
    row_number: int
    nomenclature: str


class MappingOneTargetRead(SQLModel):
    nomenclature_guid: str
    group: str | None
    group_code: str | None
    view: str | None
    view_code: str | None
    material_code: str | None
    nomenclature: str
    similarity_score: float


class MappingOneNomenclatureRead(SQLModel):
    row_number: int
    internal_group: str
    group: str | None
    group_code: str | None
    view: str | None
    view_code: str | None
    nomenclature: str
    material_code: str | None
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
