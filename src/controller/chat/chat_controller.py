from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model.chat import chat_model
from model.auth.auth_model import get_current_user
from repository.chat import chat_repository
from scheme.chat.chat_scheme import ChatRead, ChatCreate
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("/{user_id}/{mode_id}", response_model=ChatRead)
@version(1)
def get_chat(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    user_id: int,
    mode_id: int
):
    """
    """
    return chat_model.get_chat_by_user_id(session, user_id, mode_id)


@router.post("", response_model=ChatRead)
@version(1)
def create_chat(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    chat: ChatCreate
):
    """
    """
    return chat_repository.create_chat(session, chat)
