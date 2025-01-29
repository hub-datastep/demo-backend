from sqlmodel import Field, SQLModel, Relationship

from scheme.mode.mode_tenant_scheme import ModeTenantLink


class TenantBase(SQLModel):
    name: str
    db_uri: str


class Tenant(TenantBase, table=True):
    __tablename__ = "tenant"

    id: int | None = Field(default=None, primary_key=True)

    users: list["User"] = Relationship(back_populates="tenant")
    modes: list["Mode"] = Relationship(back_populates="tenants", link_model=ModeTenantLink)
    prompts: list["Prompt"] = Relationship(back_populates="tenant")
    active_prompt: "Prompt" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "and_(Tenant.id == Prompt.tenant_id, Prompt.is_active == True)",
        },
    )


class TenantCreate(TenantBase):
    modes: list[int]


class TenantUpdate(TenantCreate):
    id: int


class TenantRead(TenantBase):
    id: int
    modes: list["Mode"]


from scheme.prompt.prompt_scheme import Prompt
from scheme.user.user_scheme import User
from scheme.mode.mode_scheme import Mode

Tenant.update_forward_refs()
TenantRead.update_forward_refs()
