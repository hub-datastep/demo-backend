from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.message_dto import MessageOutDto, MessageCreateDto
from dto.user_dto import UserDto
from repository.message_repository import message_repository
from service.auth_service import AuthService

router = APIRouter(
    prefix="/message",
    tags=["message"],
)


@router.post("", response_model=MessageOutDto)
@version(1)
async def create_message(body: MessageCreateDto, current_user: UserDto = Depends(AuthService.get_current_user)):
    return message_repository.create(body)


@router.delete("/{chat_id}")
@version(1)
async def clear_all_messages_by_chat_id(chat_id: int, current_user: UserDto = Depends(AuthService.get_current_user)):
    return message_repository.clear(chat_id)
