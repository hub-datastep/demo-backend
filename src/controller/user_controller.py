from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.user_dto import UserDto
from service.auth_service import AuthService

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.get("/current")
@version(1)
async def get_current_user(current_user: UserDto = Depends(AuthService.get_current_user)):
    return current_user
