from sqlmodel import SQLModel


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
    nomenclature_params: list[dict]
    mappings: list[MappingOneTargetRead] | None
    similar_mappings: list[MappingOneTargetRead] | None


class MappingNomenclaturesUpload(SQLModel):
    nomenclatures: list[MappingOneNomenclatureUpload]
    most_similar_count: int = 3
    chunk_size: int = 100
    ner: bool = True


class MappingNomenclaturesResultRead(SQLModel):
    job_id: str
    ready_count: int | None
    total_count: int | None
    general_status: str
    nomenclatures: list[MappingOneNomenclatureRead] | None
