from sqlmodel import SQLModel, Field, Relationship


class EmergencyClassificationConfigBase(SQLModel):
    is_use_emergency_classification: bool = Field(default=True)
    is_use_order_updating: bool = Field(default=True)


class EmergencyClassificationConfig(EmergencyClassificationConfigBase, table=True):
    __tablename__ = "emergency_classification_config"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    user: "User" = Relationship(back_populates="emergency_classification_config")


from scheme.user.user_scheme import User

EmergencyClassificationConfig.update_forward_refs()
