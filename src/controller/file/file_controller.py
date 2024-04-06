import io
import re
import tempfile

import pdfplumber
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
    """
    """
    return get_all_filenames_by_tenant_id(session, current_user.tenants[0].id)

@router.post("/extract_data")
async def extract_data_from_pdf(fileObject: UploadFile, with_metadata: bool = False):
    result_list = []

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(fileObject.file.read())
        temp_file.seek(0)


    with pdfplumber.open(temp_file.name) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()

            for table_num, table in enumerate(tables):
                if not table:  # Проверяем, что таблица не пустая
                    continue

                column_names = [name.lower() if name else "" for name in table[0]]

                nomenclature_column_index = None
                for i, col_name in enumerate(column_names):
                    nomenclature_pattern = r"\bтовары\b|\bнаименование\b|\bпозиция\b|\bноменклатура\b|\bработы\b|\bуслуги\b|\bпредмет счета\b"
                    if re.search(nomenclature_pattern, col_name, flags=re.IGNORECASE):
                        nomenclature_column_index = i
                        break

                if nomenclature_column_index is not None:
                    for row in table[1:]:
                        if nomenclature_column_index < len(row):
                            nomenclature = row[nomenclature_column_index]
                            if with_metadata:
                                metadata = {column_name: row[col_num] for col_num, column_name in
                                            enumerate(column_names) if col_num != nomenclature_column_index}
                                result_list.append({"Nomenclature": nomenclature, "Metadata": metadata})
                            else:
                                result_list.append(nomenclature)

    return result_list


@router.post("")
@version(1)
def upload_file(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    fileObject: UploadFile
):
    """
    """
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
