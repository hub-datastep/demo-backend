from pydantic import BaseModel


class NomenclatureMappingUpdateDto(BaseModel):
    id: int
    correctness: str


class NomenclatureMappingDto(BaseModel):
    nomenclature: str
    group: str
    mapping: str


class NomenclatureMappingJobDto(BaseModel):
    status: str
    source: str
    mappings: list[NomenclatureMappingDto] | None = None
