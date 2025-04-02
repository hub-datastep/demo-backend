from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel


class OrderClassificationConfigBase(SQLModel):
    rules_by_classes: dict | None = Field(default=None, sa_column=Column(JSONB))
    client: str | None = Field(default=None)
    is_use_order_classification: bool | None = Field(default=False)
    is_use_order_updating: bool | None = Field(default=False)
    is_use_send_message: bool | None = Field(default=False)
    responsible_users: list[dict] | None = Field(default=None, sa_column=Column(JSONB))
    messages_templates: list[dict] | None = Field(default=None, sa_column=Column(JSONB))


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
    # User ID in Domyland
    user_id: str
    # Some name of the User
    name: str | None = None
    order_class: str | None = None
    # TODO: decide if we need store classes for users
    # order_classes_list: list[str] | None = []
    # Addresses (Оbjects) list where Responsible User works
    address_list: list[str] | None = None
    # Username in Telegram
    telegram_username: str | None = None
    telegram_chat_id: str | None = None
    telegram_thread_id: int | None = None
    is_disabled: bool | None = None


class MessageTemplate(SQLModel):
    # Название шаблона
    name: str | None = None
    # Описание шаблона
    description: str | None = None
    # Текст шаблона
    text: str | None = None
    # Можно ли использовать шаблон или нет
    is_disabled: bool | None = None
    # Классы заявок, для которых можно использовать шаблон
    order_classes: list[str] | None = []


from scheme.user.user_scheme import User

OrderClassificationConfig.update_forward_refs()
