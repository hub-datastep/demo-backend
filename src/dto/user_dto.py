from pydantic import BaseModel


class UserDto(BaseModel):
    id: str
    email: str
    tenant_id: int
    available_modes: list[str]


class UserForTenantDto(BaseModel):
    user_id: str
    email: str
