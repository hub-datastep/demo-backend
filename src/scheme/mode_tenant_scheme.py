from sqlmodel import SQLModel, Field


class ModeTenantLink(SQLModel, table=True):
    __tablename__ = "mode_tenant"

    mode_id: int = Field(
        foreign_key="mode.id", primary_key=True
    )
    tenant_id: int = Field(
        foreign_key="tenant.id", primary_key=True
    )
