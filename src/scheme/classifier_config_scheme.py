from sqlmodel import SQLModel, Field, Relationship

# конфиг для конфигурации шагов в пайплайне классификатора
class ClassifierConfigBase(SQLModel):
    # использовать ли часть пайплайна классификатора с кейвордами
    is_use_keywords_detection: bool


class ClassifierConfig(ClassifierConfigBase, table=True):
    __tablename__ = "classifier_config"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="classifier_config")


class ClassifierConfigCreate(ClassifierConfigBase):
    pass


class ClassifierConfigRead(ClassifierConfigBase):
    id: int


from scheme.user_scheme import User