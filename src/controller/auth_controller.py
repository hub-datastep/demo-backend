from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_versioning import version

from dto.auth_dto import AuthDto
from dto.user_dto import UserDto
from service.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/sign_in")
@version(1)
async def sign_in(form_data: OAuth2PasswordRequestForm = Depends()) -> AuthDto:
    return AuthService.sign_in(username=form_data.username, password=form_data.password)


@router.get("/users/me")
@version(1)
async def read_users_me(current_user: UserDto = Depends(AuthService.get_current_user)) -> UserDto:
    return current_user
