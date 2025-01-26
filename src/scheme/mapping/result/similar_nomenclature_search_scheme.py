from sqlmodel import SQLModel


class SimilarNomenclatureSearch(SQLModel):
    name: str


class SimilarNomenclature(SQLModel):
    id: int
    name: str
    material_code: str
