from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from middleware.mode_middleware import modes_required, TenantMode
from model.auth.auth_model import get_current_user
from model.chat import chat_model
from repository.chat import chat_repository
from scheme.chat.chat_scheme import ChatRead, ChatCreate
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("/{user_id}/{mode_id}", response_model=ChatRead)
@version(1)
@modes_required([TenantMode.DB, TenantMode.DOCS])
def get_chat(
    user_id: int,
    mode_id: int,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    """
    return chat_model.get_chat_by_user_id(session, user_id, mode_id)


@router.post("", response_model=ChatRead)
@version(1)
@modes_required([TenantMode.DB, TenantMode.DOCS])
def create_chat(
    chat: ChatCreate,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    """
    return chat_repository.create_chat(session, chat)
