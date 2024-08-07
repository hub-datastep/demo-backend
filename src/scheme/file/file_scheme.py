from sqlmodel import SQLModel, Field


class FileBase(SQLModel):
    original_filename: str
    storage_filename: str
    file_path: str
    description: str | None


class File(FileBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")


class FileCreate(FileBase):
    tenant_id: int


class FileRead(FileBase):
    id: int


class DataExtract(SQLModel):
    nomenclature: str | None
    file_metadata: dict[str, str] | None


class KnowledgeBaseFile(SQLModel):
    original_filename: str
    file_description: str
    storage_filename: str
