from fastapi import APIRouter, Depends, UploadFile
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from middleware.mode_middleware import TenantMode, modes_required
from model.auth.auth_model import get_current_user
from model.file import file_model, utd_file_model
from model.file.file_model import extract_data_from_invoice
from repository.file.file_repository import get_all_filenames_by_tenant_id
from scheme.file.file_scheme import FileRead, DataExtract, File
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("", response_model=list[FileRead])
@version(1)
@modes_required([TenantMode.DOCS])
def get_all_files(
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    """
    return get_all_filenames_by_tenant_id(session, current_user.tenant_id)


@router.post("/extract_data", response_model=list[DataExtract])
@version(1)
@modes_required([TenantMode.CLASSIFIER])
def extract_data_invoice(
    file_object: UploadFile,
    with_metadata: bool = False,
    current_user: UserRead = Depends(get_current_user),
):
    return extract_data_from_invoice(file_object, with_metadata)


@router.post("/extract/utd", response_model=list[str])
@version(1)
@modes_required([TenantMode.CLASSIFIER])
def extract_utd_nomenclatures(
    file_object: UploadFile,
    current_user: UserRead = Depends(get_current_user),
):
    return utd_file_model.extract_noms_from_utd(file_object)


@router.post("", response_model=File)
@version(1)
@modes_required([TenantMode.DOCS])
def upload_file(
    file_object: UploadFile,
    is_knowledge_base: bool,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    """
    tenant_id = current_user.tenant_id
    # TODO: В контроллере не должно быть логики, перенести генерацию описания в save_file
    # description = get_file_description(file_object)
    description = ""
    return file_model.save_file(session, file_object, tenant_id, description, is_knowledge_base)


@router.delete("/{file_id}")
@version(1)
@modes_required([TenantMode.DOCS])
def delete_file(
    file_id: int,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return file_model.delete_file(session, file_id)
