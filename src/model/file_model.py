import os
import re
import shutil
import tempfile
from datetime import datetime
from typing import BinaryIO

import pdfplumber
from fastapi import UploadFile
from sqlmodel import Session

from datastep.components import datastep_faiss, datastep_multivector
from exception.file_not_found_exception import FileNotFoundException
from infra.redis_queue import get_redis_queue, QueueName, MAX_JOB_TIMEOUT
from repository import file_repository
from scheme.file_scheme import File, DataExtract, FileCreate
from scheme.nomenclature_scheme import JobIdRead
from util.files_paths import get_file_folder_path

nomenclature_pattern = r"\bтовары\b|\bнаименование\b|\bпозиция\b|\bноменклатура\b|\bработы\b|\bуслуги\b|\bпредмет счета\b"


def _save_document_to_vectorstores(storage_filename: str):
    datastep_faiss.save_document(storage_filename)
    datastep_multivector.save_document(storage_filename)


def save_file_to_vectorstores(file: File, user_id: int) -> JobIdRead:
    queue = get_redis_queue(name=QueueName.DOCUMENTS)
    job = queue.enqueue(
        _save_document_to_vectorstores,
        file.storage_filename,
        result_ttl=-1,
        job_timeout=MAX_JOB_TIMEOUT,
    )
    job.meta["user_id"] = user_id
    job.meta["file_id"] = file.id
    job.save_meta()
    return JobIdRead(job_id=job.id)


def save_file_locally(file: BinaryIO, filename: str):
    file_folder_path = get_file_folder_path(filename)
    print(f"filename: {filename}")

    file_path = f"{file_folder_path}/{filename}"
    print(f"file_path: {file_path}")

    # Create folder if not exists
    os.makedirs(f"{file_folder_path}", exist_ok=True)

    # Save file to folder
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file, buffer)


def sanitize_filename(filename):
    # Remove forbidden characters from a given filename
    forbidden_chars_pattern = re.compile(r'[\\/:"*?<>|]')
    sanitized_filename = re.sub(forbidden_chars_pattern, '_', filename)
    return sanitized_filename


def get_unique_filename(original_filename: str) -> str:
    # Split the original filename into name and extension
    name, extension = os.path.splitext(original_filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{name}_{timestamp}{extension}"
    return unique_filename


def save_file(session: Session, file_object: UploadFile, tenant_id: int) -> File:
    storage_filename = get_unique_filename(sanitize_filename(file_object.filename))

    save_file_locally(file_object.file, storage_filename)
    _save_document_to_vectorstores(storage_filename)

    file_folder_path = get_file_folder_path(storage_filename)
    file_create = FileCreate(
        original_filename=file_object.filename,
        storage_filename=storage_filename,
        tenant_id=tenant_id,
        file_path=f"{file_folder_path}/{storage_filename}"
    )
    file = file_repository.save_file(session, file_create)
    return file


def extract_data_from_pdf(file_object, with_metadata=False) -> list[str]:
    result_list = []

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_object.file.read())
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
                                result_list.append(DataExtract(nomenclature=nomenclature, file_metadata=metadata))
                            else:
                                result_list.append(nomenclature)

    return result_list


def delete_file_locally(filename: str):
    file_dir_path = get_file_folder_path(filename)
    if file_dir_path.exists():
        shutil.rmtree(file_dir_path)


def get_file_by_id(session: Session, file_id: int):
    file = file_repository.get_file_by_id(session, file_id)

    if file is None:
        raise FileNotFoundException(f"File with ID {file_id} not found.")

    return file


def delete_file(session: Session, file_id: int):
    file = get_file_by_id(session, file_id)
    file_repository.delete_file(session, file)
    delete_file_locally(file.storage_filename)
