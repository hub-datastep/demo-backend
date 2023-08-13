from fastapi import APIRouter

from dto.message_dto import MessageOutDto, MessageCreateDto
from repository.message_repository import message_repository

router = APIRouter(
    prefix="/message",
    tags=["message"],
)


@router.post("/", response_model=MessageOutDto)
async def create_message(body: MessageCreateDto):
    return message_repository.create(body)
