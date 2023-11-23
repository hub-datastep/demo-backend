from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from dto.message_dto import MessageOutDto, MessageCreateDto
from dto.user_dto import UserDto
from infra.database import get_session
from repository import message_repository
from scheme.chat_scheme import ChatRead
from scheme.message_scheme import MessageRead, MessageCreate

router = APIRouter(
    prefix="/message",
    tags=["message"],
)


@router.post("", response_model=MessageRead)
@version(1)
def create_message(*, session: Session = Depends(get_session), message: MessageCreate):
    return message_repository.create_message(session, message)


@router.delete("/{chat_id}", response_model=ChatRead)
@version(1)
def clear_all_messages_by_chat_id(*, session: Session = Depends(get_session), chat_id: int):
    return message_repository.drop_all_messages_by_chat_id(session, chat_id)
