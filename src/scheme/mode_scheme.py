from sqlmodel import SQLModel, Field, Relationship

from scheme.mode_tenant_scheme import ModeTenantLink


class ModeBase(SQLModel):
    name: str


class Mode(ModeBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tenants: list["Tenant"] = Relationship(back_populates="modes", link_model=ModeTenantLink)


class ModeCreate(ModeBase):
    pass


class ModeRead(ModeBase):
    id: int


from scheme.tenant_scheme import Tenant