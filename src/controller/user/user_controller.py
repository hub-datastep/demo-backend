from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model.auth.auth_model import get_current_user
from repository.user import user_repository
from scheme.user.user_scheme import UserCreate, UserRead, User, UserUpdate

router = APIRouter()


@router.post("", response_model=UserRead)
@version(1)
def create_user(
    user: UserCreate,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    """
    return user_repository.create_user(session, user)


@router.put("", response_model=UserRead)
@version(1)
def update_user(
    user: UserUpdate,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    """
    return user_repository.update_user(session, user)


@router.get("/current", response_model=UserRead)
@version(1)
def get_current_user(current_user: User = Depends(get_current_user)):
    """
    """
    return current_user
