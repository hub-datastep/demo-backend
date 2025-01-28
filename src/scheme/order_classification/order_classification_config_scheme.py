from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field, Relationship


class OrderClassificationClient:
    VYSOTA = "vysota"


class OrderClassificationConfigBase(SQLModel):
    rules_by_classes: dict | None = Field(default=None, sa_column=Column(JSONB))
    client: str | None = Field(default=None)
    is_use_order_classification: bool | None = Field(default=False)
    is_use_order_updating: bool | None = Field(default=False)
    responsible_users: list[dict] | None = Field(default=None, sa_column=Column(JSONB))


class OrderClassificationConfig(OrderClassificationConfigBase, table=True):
    __tablename__ = "order_classification_config"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(foreign_key="user.id")

    user: "User" = Relationship(back_populates="order_classification_config")


class RulesWithParams(SQLModel):
    rules: list[str]
    exclusion_rules: list[str] | None = None
    is_use_classification: bool | None = None
    is_use_order_updating: bool | None = None


class ResponsibleUser(SQLModel):
    user_id: str
    name: str | None = None
    is_disabled: bool | None = None


class ResponsibleUserWithAddresses(ResponsibleUser):
    address_list: list[str]


from scheme.user.user_scheme import User

OrderClassificationConfig.update_forward_refs()
