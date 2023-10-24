from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.file_upload_task_dto import FileUploadTaskDto
from model import file_model
from repository import file_upload_task_repository, file_repository
from dto.user_dto import UserDto
from service.auth_service import AuthService

router = APIRouter(
    prefix="/task",
    tags=["task"],
)


@router.get("/file_upload/active", response_model=list[FileUploadTaskDto])
@version(1)
async def get_active_file_upload_tasks(current_user: UserDto = Depends(AuthService.get_current_user)):
    return file_upload_task_repository.get_active_tasks(current_user.id)


@router.delete("/file_upload/{task_id}", response_model=FileUploadTaskDto)
@version(1)
async def interrupt_task_by_id(task_id: int, current_user: UserDto = Depends(AuthService.get_current_user)):
    file = file_repository.get_file_by_task_id(task_id)
    file_model.delete_file(file)
    return file_upload_task_repository.update(task_id, {"status": "interrupted"})
