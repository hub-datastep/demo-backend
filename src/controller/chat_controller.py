from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from repository import chat_repository
from scheme.chat_scheme import ChatRead, ChatCreate


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.get("/{user_id}", response_model=ChatRead)
@version(1)
def get_chat(*, session: Session = Depends(get_session), user_id: int):
    return chat_repository.get_chat_by_user_id(session, user_id)


@router.post("", response_model=ChatRead)
@version(1)
def create_chat(*, session: Session = Depends(get_session), chat: ChatCreate):
    return chat_repository.create_chat(session, chat)
