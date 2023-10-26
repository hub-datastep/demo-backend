from datetime import datetime

from pydantic import BaseModel

class TenantCreateDto(BaseModel):
    name: str
    logo: str
    db_uri: str

class TenantDto(TenantCreateDto):
    id: int
    created_at: datetime
    