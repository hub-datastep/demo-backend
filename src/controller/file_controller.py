from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.file_dto import FileDto
from dto.user_dto import UserDto
from repository import file_repository
from service.auth_service import AuthService

router = APIRouter(
    prefix="/file",
    tags=["file"],
)


@router.get("", response_model=list[FileDto])
@version(1)
async def get_all_files(current_user: UserDto = Depends(AuthService.get_current_user)):
    return file_repository.get_all_filenames_ru()
