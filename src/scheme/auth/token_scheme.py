from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str
    # refresh_token: str
    token_type: str = "bearer"


class TokenData(SQLModel):
    user_id: int
