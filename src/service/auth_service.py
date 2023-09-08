from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from gotrue import UserResponse
from gotrue.errors import AuthApiError

from dto.auth_dto import AuthDto
from dto.user_dto import UserDto
from infra.supabase import supabase


class AuthService:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/sign_in")

    @classmethod
    def sign_in(cls, username: str, password: str) -> AuthDto:
        try:
            (_, (_, session)) = supabase.auth.sign_in_with_password({"email": username, "password": password})
            return AuthDto(
                access_token=session.access_token,
                refresh_token=session.refresh_token
            )
        except AuthApiError:
            raise HTTPException(status_code=401)

    @classmethod
    def get_current_user(cls, token: str = Depends(oauth2_scheme)) -> UserDto:
        try:
            user_response: UserResponse = supabase.auth.get_user(token)
            return UserDto(email=user_response.user.email, id=user_response.user.id)
        except AuthApiError as e:
            raise HTTPException(status_code=e.status, detail=e.message)
