from sqlmodel import SQLModel, Field, Relationship


class RoleBase(SQLModel):
    name: str


class Role(RoleBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    users: list["User"] = Relationship(back_populates="role")


from scheme.user.user_scheme import User

Role.update_forward_refs()
