from fastapi import APIRouter, Depends, UploadFile
from fastapi_versioning import version

from dto.user_dto import UserDto
from model import source_model
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


@router.post("/{chat_id}")
@version(1)
async def upload_source(chat_id: int, fileObject: UploadFile, current_user: UserDto = Depends(AuthService.get_current_user)):
    return source_model.save_source(chat_id, fileObject)
