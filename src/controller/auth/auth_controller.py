from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from infra.database import get_session
from model.auth import auth_model
from scheme.auth.token_scheme import Token

router = APIRouter()


@router.post("/sign_in", response_model=Token)
def sign_in(
    session: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    """
    token = auth_model.sign_in(session, form_data.username, form_data.password)
    return token
