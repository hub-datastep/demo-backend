from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_versioning import version

from infra.database import get_session
from model import auth_model
from model.auth_model import get_current_user
from scheme.token_scheme import Token
from scheme.user_scheme import User, UserRead
from sqlmodel import Session

router = APIRouter(
    prefix="/auth"
)


@router.post("/sign_in", response_model=Token)
async def sign_in(session: Session = Depends(get_session), form_data: OAuth2PasswordRequestForm = Depends()):
    token = auth_model.sign_in(session, form_data.username, form_data.password)
    return token


# @router.post("/token", response_model=Token)
# async def get_new_token(*, session: Session = Depends(get_session), refresh_token: TokenRefresh):
#     token = auth_model.get_refreshed_token(session, refresh_token)
#     return token


@router.get("/users/me", response_model=UserRead)
@version(1)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
