from sqlmodel import SQLModel


class SimilarNomenclatureSearch(SQLModel):
    name: str
    group: str | None = None
    is_group: bool | None = None
    limit: int | None = None
    offset: int | None = None


class SimilarNomenclature(SQLModel):
    id: int
    name: str
    group: str | None = None
    material_code: str
