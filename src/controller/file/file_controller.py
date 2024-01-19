from fastapi import APIRouter, Depends, UploadFile
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model import file_model
from model.auth_model import get_current_user
from repository.file_repository import get_all_filenames_by_tenant_id
from scheme.file_scheme import FileRead
from scheme.user_scheme import UserRead

router = APIRouter()


@router.get("", response_model=list[FileRead])
@version(1)
def get_all_files(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return get_all_filenames_by_tenant_id(session, current_user.tenants[0].id)


@router.post("")
@version(1)
def upload_file(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    fileObject: UploadFile
):
    job = file_model.process_file(session, fileObject, current_user.id, current_user.tenants[0].id)
    return ""
    # return FileUploadTaskDto(
    #     id=job.id,
    #     # status=job.get_status(refresh=True),
    #     progress=job.get_meta(refresh=True).get("progress", None),
    #     full_work=job.get_meta(refresh=True).get("full_work", None)
    # )


# @router.delete("/")
# @version(1)
# def delete_file(
#     *,
#     current_user: UserRead = Depends(get_current_user),
#     body: FileOutDto
# ):
#     return file_model.delete_file(body)
