from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship


class PromptBase(SQLModel):
    prompt: str
    is_active: bool = False
    table: str


class Prompt(PromptBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    tenant: "Tenant" = Relationship(back_populates="prompts")
    created_at: datetime | None = Field(default=datetime.utcnow())
    updated_at: datetime | None = Field(default_factory=datetime.utcnow)


class PromptCreate(PromptBase):
    tenant_id: int


class PromptUpdate(PromptBase):
    pass


class PromptRead(PromptBase):
    id: int


from scheme.tenant_scheme import Tenant