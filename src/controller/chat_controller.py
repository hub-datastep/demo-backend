from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.chat_dto import ChatOutDto, ChatCreateDto
from dto.user_dto import UserDto
from repository.chat_repository import chat_repository
from service.auth_service import AuthService

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.get("/{user_id}", response_model=ChatOutDto)
@version(1)
def get_chat(user_id: str, current_user: UserDto = Depends(AuthService.get_current_user)):
    return chat_repository.fetch_by_user_id(user_id)


@router.post("", response_model=ChatOutDto)
@version(1)
def create_chat(body: ChatCreateDto, current_user: UserDto = Depends(AuthService.get_current_user)):
    return chat_repository.create(body)
