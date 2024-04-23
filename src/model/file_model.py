import os
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import pdfplumber
from fastapi import UploadFile
from redis import Redis
from rq import Queue
from rq.job import Job
from sqlmodel import Session

from datastep.components import datastep_faiss, datastep_multivector
from infra.env import REDIS_PASSWORD, REDIS_HOST
from repository import file_repository
from scheme.file_scheme import File, FileCreate, DataExtract

nomenclature_pattern = r"\bтовары\b|\bнаименование\b|\bпозиция\b|\bноменклатура\b|\bработы\b|\bуслуги\b|\bпредмет счета\b"


def save_file_vectorstore_(storage_filename):
    try:
        datastep_faiss.save_document(storage_filename)
        datastep_multivector.save_document(storage_filename)
    except Exception as e:
        # delete_file(file)
        raise e


def save_file_vectorstore(file_db: File, user_id: int) -> Job:
    redis = Redis(host=REDIS_HOST, password=REDIS_PASSWORD)
    q = Queue("document", connection=redis)
    job = q.enqueue(save_file_vectorstore_, file_db.storage_filename, result_ttl=-1, job_timeout="60m")
    job.meta["user_id"] = user_id
    job.meta["file_id"] = file_db.id
    job.save_meta()
    return job


def save_file_local(file: UploadFile, filename: str):
    data_folder_path = Path(__file__).parent / "../../data"
    # Split the original filename into name and extension
    file_folder_name, _ = os.path.splitext(filename)
    file_folder_path = data_folder_path / file_folder_name

    if not os.path.exists(file_folder_path):
        os.makedirs(file_folder_path)

    file_path = file_folder_path / filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except:
        pass


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


def process_file(session: Session, file_object: UploadFile, user_id: int, tenant_id: int) -> Job:
    storage_filename = get_unique_filename(sanitize_filename(file_object.filename))
    save_file_local(file_object, storage_filename)

    filename, _ = os.path.splitext(storage_filename)
    file_create = FileCreate(
        original_filename=file_object.filename,
        storage_filename=storage_filename,
        tenant_id=tenant_id,
        file_path=f"{filename}/{storage_filename}"
    )
    file_db = file_repository.save_file(session, file_create)
    return save_file_vectorstore(file_db, user_id)


def get_store_file_path(source_id: str) -> str:
    return f"{Path(__file__).parent.resolve()}/../../data/{source_id}"


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


# def delete_local_store(filename):
#     try:
#         store_file_path = get_store_file_path(filename)
#         shutil.rmtree(store_file_path)
#     except FileNotFoundError:
#         pass


# def delete_file(body: FileDto):
#     file_repository.update({"id": body.id}, {"status": "deleted"})
#     if not file_repository.is_file_exists_in_other_chats(body.chat_id, body.name_ru):
#         delete_file_from_supastorage(body.name_en)
#         delete_local_store(body.name_en)


if __name__ == "__main__":
    data_folder = Path(__file__).parent / Path("../../data")
    print(data_folder)
    file = data_folder / "etm_231223_9_result.csv"
    content = file.read_text()
