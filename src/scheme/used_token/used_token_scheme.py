from datetime import datetime

from sqlmodel import SQLModel, Field


class UsedToken(SQLModel, table=True):
    __tablename__ = "used_token"

    id: int | None = Field(default=None, primary_key=True)
    tokens_count: int
    tenant_id: int = Field(foreign_key="tenant.id")
    user_id: int = Field(foreign_key="user.id")
    used_at: datetime | None = Field(default_factory=datetime.utcnow)
