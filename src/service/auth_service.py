from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from gotrue import UserResponse
from gotrue.errors import AuthApiError
from infra.database import get_session
from sqlmodel import Session

from dto.auth_dto import AuthDto
from dto.user_dto import UserDto
from dto.config_dto import DatabasePredictionConfigDto
from infra.supabase import supabase
from repository import config_repository, user_repository
# from repository.tenant_repository import tenant_repository
from scheme.user_scheme import UserRead


class AuthService:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/sign_in")

    @classmethod
    def sign_in(cls, username: str, password: str) -> AuthDto:
        try:
            (_, (_, session)) = supabase.auth.sign_in_with_password({
                "email": username,
                "password": password
            })
            return AuthDto(
                access_token=session.access_token,
                refresh_token=session.refresh_token
            )
        except AuthApiError:
            raise HTTPException(status_code=401)

    @classmethod
    def get_database_prediction_config(cls, user_id: str) -> DatabasePredictionConfigDto:
        return config_repository.get_database_prediction_config(user_id)

    @classmethod
    def get_current_user(cls, token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> UserRead:
        try:
            user_response: UserResponse = supabase.auth.get_user(token)
            user = user_repository.get_user_by_id(session, user_response.user.id)
            return UserRead.from_orm(user)
            # tenant_id = tenant_repository.get_tenant_id_by_user_id(user_response.user.id)
            # available_modes = tenant_repository.get_modes_by_tenant_id(tenant_id)
        except AuthApiError as e:
            raise HTTPException(status_code=e.status, detail=e.message)
