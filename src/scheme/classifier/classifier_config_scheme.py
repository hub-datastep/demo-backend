from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class ClassifierConfigBase(SQLModel):
    is_use_keywords_detection: bool
    chroma_collection_name: Optional[str] = None


class ClassifierConfig(ClassifierConfigBase, table=True):
    __tablename__ = "classifier_config"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="classifier_config")


from scheme.user.user_scheme import User

ClassifierConfig.update_forward_refs()
