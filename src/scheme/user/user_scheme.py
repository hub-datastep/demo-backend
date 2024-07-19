from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from scheme.user.user_tenant_scheme import UserTenantLink


class UserBase(SQLModel):
    username: str


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password: str
    tenants: list["Tenant"] = Relationship(back_populates="users", link_model=UserTenantLink)
    chat: "Chat" = Relationship(back_populates="user")
    database_prediction_config: "DatabasePredictionConfig" = Relationship(back_populates="user")
    classifier_config: "ClassifierConfig" = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str
    tenant_id: int


class UserUpdate(UserCreate):
    id: int


class UserRead(UserBase):
    id: int
    tenants: list["TenantRead"]
    database_prediction_config: Optional["DatabasePredictionConfig"] = None
    classifier_config: Optional["ClassifierConfig"] = None


from scheme.chat.chat_scheme import Chat
from scheme.classifier.classifier_config_scheme import ClassifierConfig
from scheme.prediction.database_prediction_config_scheme import DatabasePredictionConfig
from scheme.tenant.tenant_scheme import Tenant, TenantRead

User.update_forward_refs()
UserRead.update_forward_refs()
