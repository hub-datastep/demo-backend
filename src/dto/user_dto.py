from pydantic import BaseModel


class UserDto(BaseModel):
    email: str
    tenant_id: int
