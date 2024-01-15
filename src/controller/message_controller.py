from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from dto.message_dto import CreateFavoriteMessageDto
from dto.user_dto import UserDto
from infra.database import get_session
from repository import message_repository
from scheme.chat_scheme import ChatRead
from scheme.message_scheme import MessageRead, MessageCreate
from service.auth_service import AuthService


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


@router.get("/favorite/{user_id}")
@version(1)
def get_favorites_list_by_user_id(user_id: str, current_user: UserDto=Depends(AuthService.get_current_user)):
    return message_repository.get_favorites_list(user_id)


@router.post("/favorite")
@version(1)
def add_message_to_favorites_list(body: CreateFavoriteMessageDto, current_user: UserDto=Depends(AuthService.get_current_user)):
    return message_repository.add_favorite_message(body)

@router.delete("/favorite/{favorite_message_id}")
@version(1)
def remove_favorite_message(favorite_message_id: int, current_user: UserDto = Depends(AuthService.get_current_user)):
    return message_repository.remove_favorite_message(favorite_message_id)
