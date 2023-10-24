from pydantic import BaseModel


class FileDto(BaseModel):
    name_ru: str
    name_en: str
    url: str
    chat_id: int | None = None
    status: str
    file_upload_task_id: int | None = None


class FileOutDto(FileDto):
    id: int


class StorageFileDto(BaseModel):
    filename: str
    fileUrl: str
