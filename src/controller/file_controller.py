from fastapi import APIRouter, Depends, UploadFile
from fastapi_versioning import version

from dto.file_dto import FileDto, FileOutDto
from dto.user_dto import UserDto
from model import file_model
from repository import file_repository
from service.auth_service import AuthService

router = APIRouter(
    prefix="/file",
    tags=["file"],
)


@router.get("/{chat_id}", response_model=list[FileOutDto])
@version(1)
async def get_all_files(chat_id: int, current_user: UserDto = Depends(AuthService.get_current_user)):
    return file_repository.get_all_filenames_ru(chat_id)


@router.post("/{chat_id}")
@version(1)
async def upload_file(chat_id: int, fileObject: UploadFile, current_user: UserDto = Depends(AuthService.get_current_user)):
    return file_model.save_file(chat_id, fileObject)

@router.delete("/")
@version(1)
async def delete_file(body: FileOutDto, current_user: UserDto = Depends(AuthService.get_current_user)):
    return file_model.delete_file(body)
