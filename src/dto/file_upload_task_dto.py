from datetime import datetime

from pydantic import BaseModel


class FileUploadTaskDto(BaseModel):
    id: int
    file_id: int
    progress: int
    full_work: int
    created_at: datetime
    status: str
