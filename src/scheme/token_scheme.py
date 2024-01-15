from sqlmodel import SQLModel


# class TokenRefresh(SQLModel):
#     refresh_token: str


class Token(SQLModel):
    access_token: str
    # refresh_token: str
    token_type: str = "bearer"


class TokenData(SQLModel):
    user_id: int
