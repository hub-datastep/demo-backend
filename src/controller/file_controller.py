from fastapi import APIRouter, Depends, UploadFile
from fastapi_versioning import version

from dto.user_dto import UserDto
from model import file_model
from service.auth_service import AuthService

router = APIRouter(
    prefix="/file",
    tags=["file"],
)


@router.post("")
@version(1)
async def upload_file(file: UploadFile, current_user: UserDto = Depends(AuthService.get_current_user)):
    return file_model.upload_file(file)
