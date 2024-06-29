from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model.auth.auth_model import get_current_user
from repository import mark_repository
from scheme.chat.mark_scheme import MarkRead, MarkCreate
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.post("", response_model=MarkRead)
@version(1)
def create_or_update_mark(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    mark: MarkCreate
):
    """
    """
    return mark_repository.create_or_update_mark(session, mark)
