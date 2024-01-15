from sqlmodel import SQLModel, Field


class FileBase(SQLModel):
    mark: bool
    name_ru: str
    name_en: str
    url: str
    status: str


class File(FileBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")


class FileCreate(FileBase):
    pass


class FileRead(FileBase):
    id: int
