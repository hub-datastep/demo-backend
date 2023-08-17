from pydantic import BaseModel


class AuthDto(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

