from pydantic import BaseModel

from dto.config_dto import DatabasePredictionConfigDto


class UserOutDto(BaseModel):
    id: str
    email: str
    tenant_id: int
    available_modes: list[str]
    database_prediction_config: DatabasePredictionConfigDto | None


class UserCreateDto(UserOutDto):
    password: str

