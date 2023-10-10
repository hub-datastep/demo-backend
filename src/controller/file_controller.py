from fastapi import APIRouter, Depends, UploadFile
from fastapi_versioning import version

from dto.file_dto import FileDto
from dto.user_dto import UserDto
from model import file_model
from repository import file_repository
from service.auth_service import AuthService

router = APIRouter(
    prefix="/file",
    tags=["file"],
)


@router.get("/{chat_id}", response_model=list[FileDto])
@version(1)
async def get_all_files(chat_id: int, current_user: UserDto = Depends(AuthService.get_current_user)):
    return file_repository.get_all_filenames_ru(chat_id)


@router.post("/{chat_id}")
@version(1)
async def upload_file(chat_id: int, fileObject: UploadFile, current_user: UserDto = Depends(AuthService.get_current_user)):
    return file_model.save_file(chat_id, fileObject)
