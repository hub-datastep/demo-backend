from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.user_dto import UserDto
from repository.logo_repository import logo_repository
from service.auth_service import AuthService
from model import tenant_logo_model

router = APIRouter(
    prefix="/logo",
    tags=["logo"],
)


@router.get("/{user_id}")
@version(1)
async def get_logo_by_tenant_id(user_id: str):
    return tenant_logo_model.get_logo(user_id)
