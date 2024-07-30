from sqlmodel import SQLModel


class AutocompleteNomenclatureNameQuery(SQLModel):
    query: str
