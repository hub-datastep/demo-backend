from datetime import datetime

from pydantic import BaseModel


class PromptEditDto(BaseModel):
    prompt: str


class PromptOutDto(PromptEditDto):
    created_at: datetime
