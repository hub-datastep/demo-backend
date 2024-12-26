from sqlalchemy import Column, ARRAY, String
from sqlmodel import SQLModel, Field, Relationship


class SolutionImitationConfigBase(SQLModel):
    prompt: str | None = Field(default=None)
    type: str | None = Field(default=None)
    input_variables: list[str] | None = Field(
        default=None,
        sa_column=Column(ARRAY(String)),
    )


class SolutionImitationConfig(SolutionImitationConfigBase, table=True):
    __tablename__ = "solution_imitation_config"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

    user: "User" = Relationship(back_populates="solution_imitation_configs")


from scheme.user.user_scheme import User

SolutionImitationConfig.update_forward_refs()
