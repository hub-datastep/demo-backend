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
    source: str | None

    def to_row(self):
        return (
            self.output,
            str(self.status),
            self.wide_group,
            self.middle_group,
            self.narrow_group,
            self.source
        )
