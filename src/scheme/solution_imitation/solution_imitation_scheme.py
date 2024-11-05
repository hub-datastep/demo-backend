from sqlmodel import SQLModel


class SolutionImitationRequest(SQLModel):
    type: str
