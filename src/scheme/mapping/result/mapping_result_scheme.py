from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field, Relationship


class MappingResultBase(SQLModel):
    iteration_id: str | None = Field(foreign_key="mapping_iteration.id")
    user_id: int | None = Field(foreign_key="user.id")
    results: dict | None = Field(sa_column=Column(JSONB))
    corrected_nomenclature: dict | None = Field(default=None, sa_column=Column(JSONB))


class MappingResult(MappingResultBase, table=True):
    __tablename__ = "mapping_result"

    id: int | None = Field(default=None, primary_key=True)

    iteration: "MappingIteration" = Relationship(back_populates="results")


class MappingResultUpdate(SQLModel):
    id: int
    mapping_nomenclature_corrected: str


class InputModel(SQLModel):
    model_name: str
    model_type: str
    material: str


class MappedCimModel(SQLModel):
    model: str
    work_type: str


from scheme.mapping.result.mapping_iteration_scheme import MappingIteration

MappingResult.update_forward_refs()
