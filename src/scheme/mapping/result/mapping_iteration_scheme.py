from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field, Relationship


class MappingIterationBase(SQLModel):
    metadatas: dict | None = Field(sa_column=Column(JSONB))
    created_at: datetime | None = Field(default_factory=datetime.utcnow)


class MappingIteration(MappingIterationBase, table=True):
    __tablename__ = "mapping_iteration"

    id: str | None = Field(default=None, primary_key=True)

    results: list["MappingResult"] = Relationship(back_populates="iteration")


class IterationWithResults(MappingIterationBase):
    id: str
    results: list["MappingResult"]


from scheme.mapping.result.mapping_result_scheme import MappingResult

MappingIteration.update_forward_refs()
IterationWithResults.update_forward_refs()
