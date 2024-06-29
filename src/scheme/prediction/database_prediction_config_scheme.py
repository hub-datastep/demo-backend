from sqlmodel import SQLModel, Field, Relationship


class DatabasePredictionConfigBase(SQLModel):
    is_data_check: bool
    is_sql_description: bool
    is_alternative_questions: bool


class DatabasePredictionConfig(DatabasePredictionConfigBase, table=True):
    __tablename__ = "database_prediction_config"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="database_prediction_config")


class DatabasePredictionConfigCreate(DatabasePredictionConfigBase):
    pass


class DatabasePredictionConfigRead(DatabasePredictionConfigBase):
    id: int


from scheme.user.user_scheme import User

DatabasePredictionConfig.update_forward_refs()
