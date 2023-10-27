from datetime import datetime

from pydantic import BaseModel


class PromptEditDto(BaseModel):
    prompt: str


class PromptDto(PromptEditDto):
    id: int
    tenant_id: int
    name: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: str | None
    updated_by: str | None
    table: str
