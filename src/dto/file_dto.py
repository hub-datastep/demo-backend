from pydantic import BaseModel


class FileDto(BaseModel):
    id: int
    name_ru: str
    name_en: str
    url: str
