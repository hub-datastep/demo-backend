from sqlmodel import SQLModel, Field, Relationship


class OrderClassificationClient:
    VYSOTA = "vysota"


class OrderClassificationConfigBase(SQLModel):
    emergency_prompt: str | None = Field(default=None)
    client: str | None = Field(default=None)
    is_use_emergency_classification: bool = Field(default=False)
    is_use_order_updating: bool = Field(default=False)


class OrderClassificationConfig(OrderClassificationConfigBase, table=True):
    __tablename__ = "order_classification_config"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    user: "User" = Relationship(back_populates="order_classification_config")


from scheme.user.user_scheme import User

OrderClassificationConfig.update_forward_refs()
