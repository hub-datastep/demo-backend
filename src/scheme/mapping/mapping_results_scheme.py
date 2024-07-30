from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field


class CustomConfig:
    arbitrary_types_allowed = True


class MappingResult(SQLModel, table=True):
    __tablename__ = "mapping_result"
    Config = CustomConfig

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    mapping_result: dict = Field(sa_column=Column(JSONB))
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    mapping_nomenclature_corrected: str | None = Field(default=None)


class NomenclatureQuery(SQLModel):
    query: str


class MappingResultUpdate(SQLModel):
    id: int
    mapping_nomenclature_corrected: str
