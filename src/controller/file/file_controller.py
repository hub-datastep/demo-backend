from fastapi import APIRouter, Depends, UploadFile
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model import file_model
from model.auth_model import get_current_user
from model.file_model import extract_data_from_pdf
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
    """
    """
    return get_all_filenames_by_tenant_id(session, current_user.tenants[0].id)


@router.post("/extract_data")
@version(1)
async def extract_data_from_pdf_controller(
    file_object: UploadFile,
    with_metadata: bool = False,
    current_user: UserRead = Depends(get_current_user),
):
    return extract_data_from_pdf(file_object, with_metadata)


@router.post("")
@version(1)
def upload_file(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    file_object: UploadFile,
):
    """
    """
    tenant_id = current_user.tenants[0].id
    return file_model.process_file(session, file_object, current_user.id, tenant_id)


@router.delete("/{file_id}")
@version(1)
def delete_file(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    file_id: int,
):
    return file_model.delete_file(session, file_id)
