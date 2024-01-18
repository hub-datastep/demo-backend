from fastapi import APIRouter, Depends, UploadFile
from fastapi_versioning import version
from sqlmodel import Session

from dto.file_dto import FileOutDto
from dto.file_upload_task_dto import FileUploadTaskDto
from dto.user_dto import UserDto
from infra.database import get_session
from model import file_model
from model.auth_model import get_current_user
from repository import file_repository
from repository.file_repository import get_all_filenames_by_tenant_id
from scheme.file_scheme import FileRead
from scheme.user_scheme import UserRead

# from service.auth_service import AuthService

router = APIRouter()


@router.get("", response_model=list[FileRead])
@version(1)
def get_all_files(
    *,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user)
):
    return get_all_filenames_by_tenant_id(session, current_user.tenants[0].id)


@router.post("")
@version(1)
def upload_file(
    *,
    session: Session = Depends(get_session),
    fileObject: UploadFile,
    current_user: UserRead = Depends(get_current_user)
):
    job = file_model.process_file(session, fileObject, current_user.id, current_user.tenants[0].id)
    return ""
    # return FileUploadTaskDto(
    #     id=job.id,
    #     # status=job.get_status(refresh=True),
    #     progress=job.get_meta(refresh=True).get("progress", None),
    #     full_work=job.get_meta(refresh=True).get("full_work", None)
    # )


@router.delete("/")
@version(1)
def delete_file(
    body: FileOutDto,
    # current_user: UserDto = Depends(AuthService.get_current_user)
):
    return file_model.delete_file(body)
