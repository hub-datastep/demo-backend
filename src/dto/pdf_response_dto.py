from pydantic import BaseModel


class PdfResponseDto(BaseModel):
    page: int
    answer: str
