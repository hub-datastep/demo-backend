from sqlmodel import Field, SQLModel, Relationship

from scheme.mode.mode_tenant_scheme import ModeTenantLink
from scheme.user.user_tenant_scheme import UserTenantLink


class TenantBase(SQLModel):
    name: str


class Tenant(TenantBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    db_uri: str
    users: list["User"] = Relationship(back_populates="tenants", link_model=UserTenantLink)
    modes: list["Mode"] = Relationship(back_populates="tenants", link_model=ModeTenantLink)
    prompts: list["Prompt"] = Relationship(back_populates="tenant")
    active_prompt: "Prompt" = Relationship(
        sa_relationship_kwargs={"primaryjoin": "and_(Tenant.id == Prompt.tenant_id, Prompt.is_active == True)"}
    )


class TenantCreate(TenantBase):
    db_uri: str
    modes: list[int]


class TenantRead(TenantBase):
    id: int
    modes: list["ModeRead"]


from scheme.prompt.prompt_scheme import Prompt
from scheme.user.user_scheme import User
from scheme.mode.mode_scheme import ModeRead, Mode

Tenant.update_forward_refs()
TenantRead.update_forward_refs()
