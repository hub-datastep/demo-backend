from pydantic import BaseModel


class FileDto(BaseModel):
    id: int
    name_ru: str
    name_en: str
    url: str
    chat_id: int | None = None


class StorageFileDto:
    filename: str
    fileUrl: str
