from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.message_dto import MessageOutDto, MessageCreateDto, FavoriteMessageDto, CreateFavoriteMessageDto
from dto.user_dto import UserDto
from repository.message_repository import message_repository
from service.auth_service import AuthService

router = APIRouter(
    prefix="/message",
    tags=["message"],
)


@router.post("", response_model=MessageOutDto)
@version(1)
def create_message(body: MessageCreateDto, current_user: UserDto = Depends(AuthService.get_current_user)):
    return message_repository.create(body)


@router.delete("/{chat_id}")
@version(1)
def clear_all_messages_by_chat_id(chat_id: int, current_user: UserDto = Depends(AuthService.get_current_user)):
    return message_repository.clear(chat_id)


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
