from pydantic import BaseModel


class FileUploadTaskDto(BaseModel):
    id: int | str
    progress: int | None
    full_work: int | None
    status: str | None
