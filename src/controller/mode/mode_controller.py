from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model.auth.auth_model import get_current_user
from repository import mode_repository
from scheme.mode.mode_scheme import ModeRead, ModeCreate
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.post("", response_model=ModeRead)
@version(1)
def create_mode(
    mode: ModeCreate,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    """
    return mode_repository.create_mode(session, mode)
