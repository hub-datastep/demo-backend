from sqlmodel import SQLModel, Field


class UserTenantLink(SQLModel, table=True):
    __tablename__ = "user_tenant"

    user_id: int = Field(
        foreign_key="user.id", primary_key=True
    )
    tenant_id: int = Field(
        foreign_key="tenant.id", primary_key=True
    )
