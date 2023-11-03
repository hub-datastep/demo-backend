from pydantic import BaseModel


class NomenclatureMappingUpdateDto(BaseModel):
    id: int
    correctness: str


class NomenclatureMappingJobOutDto(BaseModel):
    id: int | None
    input: str
    output: str | None
    status: str | None = None
    correctness: str | None = None
    wide_group: str | None
    middle_group: str | None
    narrow_group: str | None
