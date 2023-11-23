from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from scheme.user_tenant_scheme import UserTenantLink


class UserBase(SQLModel):
    username: str


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password: str
    tenants: list["Tenant"] = Relationship(back_populates="users", link_model=UserTenantLink)
    chat: "Chat" = Relationship(back_populates="user")
    database_prediction_config: "DatabasePredictionConfig" = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str
    tenant_id: int


class UserRead(UserBase):
    id: int
    tenants: list["TenantRead"]
    database_prediction_config: Optional["DatabasePredictionConfig"] = None


from scheme.tenant_scheme import Tenant, TenantRead
from scheme.chat_scheme import Chat
from scheme.database_prediction_config_scheme import DatabasePredictionConfig

UserRead.update_forward_refs()
