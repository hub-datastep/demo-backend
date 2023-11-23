from sqlmodel import Field, SQLModel, Relationship

from scheme.mode_tenant_scheme import ModeTenantLink
from scheme.user_tenant_scheme import UserTenantLink


class TenantBase(SQLModel):
    name: str
    logo: str
    is_last: bool = False


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


class TenantRead(TenantBase):
    id: int
    modes: list["ModeRead"]


from scheme.user_scheme import User
from scheme.mode_scheme import Mode, ModeRead
from scheme.prompt_scheme import Prompt

TenantRead.update_forward_refs()
