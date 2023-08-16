from fastapi import APIRouter

from dto.chat_dto import ChatOutDto, ChatCreateDto
from repository.chat_repository import chat_repository

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.get("/{user_id}", response_model=ChatOutDto)
async def get_chat(user_id: str):
    return chat_repository.fetch_by_user_id(user_id)


@router.post("", response_model=ChatOutDto)
async def create_chat(body: ChatCreateDto):
    return chat_repository.create(body)
