from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.source_dto import SourceCreateDto
from dto.user_dto import UserDto
from repository.source_repository import source_repository
from service.auth_service import AuthService

router = APIRouter(
    prefix="/source",
    tags=["source"],
)


@router.get("/{chat_id}")
@version(1)
async def get_all_sources(chat_id: int, current_user: UserDto = Depends(AuthService.get_current_user)):
    return source_repository.get_all_sources(chat_id)


@router.get("/last/{chat_id}")
@version(1)
async def get_last_source(chat_id: int, current_user: UserDto = Depends(AuthService.get_current_user)):
    return source_repository.get_last_source(chat_id)


@router.post("")
@version(1)
async def save_source(body: SourceCreateDto, current_user: UserDto = Depends(AuthService.get_current_user)):
    return source_repository.save_source(body)
