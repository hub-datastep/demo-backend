from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class UserBase(SQLModel):
    username: str
    tenant_id: int | None = Field(default=None, foreign_key="tenant.id")
    role_id: int | None = Field(default=None, foreign_key="role.id")


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password: str

    tenant: "Tenant" = Relationship(
        back_populates="users",
    )
    role: "Role" = Relationship(
        back_populates="users",
    )

    database_prediction_config: "DatabasePredictionConfig" = Relationship(
        back_populates="user",
    )
    classifier_config: "ClassifierConfig" = Relationship(
        back_populates="user",
    )
    order_classification_config: "OrderClassificationConfig" = Relationship(
        back_populates="user",
    )
    solution_imitation_configs: list["SolutionImitationConfig"] = Relationship(
        back_populates="user",
    )

    chat: "Chat" = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str


class UserUpdate(UserCreate):
    id: int


class UserRead(UserBase):
    id: int
    tenant: Optional["TenantRead"] = None
    role: Optional["Role"] = None
    database_prediction_config: Optional["DatabasePredictionConfig"] = None
    classifier_config: Optional["ClassifierConfig"] = None


from scheme.chat.chat_scheme import Chat
from scheme.classifier.classifier_config_scheme import ClassifierConfig
from scheme.prediction.database_prediction_config_scheme import DatabasePredictionConfig
from scheme.tenant.tenant_scheme import Tenant, TenantRead
from scheme.role.role_scheme import Role
from scheme.order_classification.order_classification_config_scheme import (
    OrderClassificationConfig,
)
from scheme.solution_imitation.solution_imitation_config_scheme import (
    SolutionImitationConfig,
)

User.update_forward_refs()
UserRead.update_forward_refs()
