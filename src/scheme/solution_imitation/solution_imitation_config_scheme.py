from sqlalchemy import Column
from sqlmodel import SQLModel, Field, Relationship
from sqlmodel import ARRAY, String


class SolutionImitationConfigBase(SQLModel):
    prompt: str | None = Field(default=None)
    type: str | None = Field(default=None)
    input_variables: list[str] | None = Field(
        default=None,
        sa_column=Column(sa_column_type=ARRAY(String)),
    )


class SolutionImitationConfig(SolutionImitationConfigBase, table=True):
    __tablename__ = "solution_imitation_config"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    user: "User" = Relationship(back_populates="solution_imitation_config")


from scheme.user.user_scheme import User

SolutionImitationConfig.update_forward_refs()
