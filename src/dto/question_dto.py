from pydantic import BaseModel


class QuestionDto(BaseModel):
    id: int | None = None
    question: str


class QuestionGetDto(BaseModel):
    tables: list[str]
    limit: int = 3
