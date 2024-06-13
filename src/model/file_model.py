import os
import re
import shutil
import tempfile
from datetime import datetime
from typing import BinaryIO, List, Optional

import pdfplumber
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader
from sqlmodel import Session

from datastep.chains.datastep_file_description_chain import get_chain
from datastep.components import datastep_faiss, datastep_multivector
from exception.file_not_found_exception import FileNotFoundException
from infra.redis_queue import get_redis_queue, QueueName, MAX_JOB_TIMEOUT
from repository import file_repository
from scheme.file_scheme import File, DataExtract, FileCreate
from scheme.nomenclature_scheme import JobIdRead
from util.files_paths import get_file_folder_path, get_file_storage_path

nomenclature_pattern = r"\bтовары\b|\bнаименование\b|\bпозиция\b|\bноменклатура\b|\bработы\b|\bуслуги\b|\bпредмет счета\b"
nomenclature_pattern_cp = r"\bнаименование товара\b|\bописание выполненных работ\b|\bоказанных услуг\b|\bимущественного права\b"


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


# Сложный момент: не знала как из fileObject вытянуть описание до того как мы его где-то сохранили
def get_file_description(file_object: UploadFile) -> str:
    with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as tmp:
        tmp.write(file_object.file.read())
        tmp_path = tmp.name

        loader = PyPDFLoader(tmp_path)
        pages = loader.load_and_split()
        doc_content = " ".join([page.page_content for page in pages])

    chain = get_chain()
    description: str = chain.run(
        document_content=doc_content,
    )

    return description


# Сложный момент 2: не понимала куда сохранять описания, так как не знала различия ме
def save_file(session: Session, file_object: UploadFile, tenant_id: int, description: str) -> File:
    storage_filename = get_unique_filename(sanitize_filename(file_object.filename))

    file_storage_path = get_file_storage_path(storage_filename)
    file_create = FileCreate(
        original_filename=file_object.filename,
        storage_filename=storage_filename,
        tenant_id=tenant_id,
        file_path=f"{file_storage_path}",
        description=description,
    )
    file = file_repository.save_file(session, file_create)

    save_file_locally(file_object.file, storage_filename)
    _save_document_to_vectorstores(storage_filename)
    return file


def extract_data_from_invoice(file_object, with_metadata=False) -> List[DataExtract]:
    result_list = []

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_object.file.read())
        temp_file.seek(0)

    with pdfplumber.open(temp_file.name) as pdf:
        all_tables = []
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            print(tables)
            for table in tables:
                if is_nomenclature_table(table):
                    column_names = [name.lower() if name else "" for name in table[0]]
                    nomenclature_column_index = get_nomenclature_column_index(column_names)
                    if nomenclature_column_index is not None:
                        print("Содержимое столбца с номенклатурой:",
                              [row[nomenclature_column_index] for row in table[1:]])
                        for row in table[1:]:  # Начинаем со второй строки
                            if nomenclature_column_index < len(row):
                                nomenclature = row[nomenclature_column_index]
                                if with_metadata:
                                    metadata = {column_names[col_num]: row[col_num] for col_num in range(len(row)) if
                                                col_num != nomenclature_column_index}
                                    result_list.append(DataExtract(nomenclature=nomenclature, file_metadata=metadata))
                                else:
                                    result_list.append(DataExtract(nomenclature=nomenclature))
                    else:
                        print("Столбец с номенклатурой не найден в таблице")
    return result_list


def is_nomenclature_table(table):
    # Ключевые слова, связанные с информацией о покупателе и продавце
    # TODO: Вынести из функции
    seller_buyer_keywords = ["продавец", "покупатель", "адрес", "инн", "кпп", "директор"]

    # Проверяем, содержит ли таблица названия колонок, соответствующие номенклатурам, по регулярному выражению
    for row in table:
        for cell in row:
            if isinstance(cell, str):
                if any(keyword in cell.lower() for keyword in seller_buyer_keywords):
                    # Если найдено ключевое слово, пропускаем эту строку и переходим к следующей
                    break
                if re.search(nomenclature_pattern, cell.lower()):
                    print("Найден подходящий столбец:", cell)
                    return True
    print("Столбец с номенклатурой не найден в таблице")
    return False


def get_nomenclature_column_index(column_names):
    # Находим индекс столбца с номенклатурой, удовлетворяющий регулярному выражению
    for i, col_name in enumerate(column_names):
        if re.search(nomenclature_pattern, col_name):
            return i
    return None


# def extract_nomenclature(table):
#     # Найдем столбец с номенклатурой
#     nomenclature_column_index = None
#     for row in table:
#         for cell in row:
#             if isinstance(cell, str) and re.search(nomenclature_pattern_cp, cell.lower()):
#                 nomenclature_column_index = row.index(cell)
#                 break
#         if nomenclature_column_index is not None:
#             break
#
#     # Если столбец с номенклатурой найден, извлечем номенклатурные данные из этого столбца
#     if nomenclature_column_index is not None:
#         nomenclatures = []
#         for row in table:
#             if len(row) > nomenclature_column_index:
#                 cell = row[nomenclature_column_index].strip()
#                 if cell:
#                     nomenclatures.append(cell)
#         return nomenclatures
#     else:
#         print("Столбец с номенклатурой не найден в таблице")
#         return []

# def parse_table(table):
#     nomenclatures = extract_nomenclature(table)
#     if nomenclatures:
#         print("Номенклатуры:", nomenclatures)
#     else:
#         print("Номенклатуры не найдены.")
#
# # Пример использования:
# parse_table(table)


def extract_and_print_table_columns(file_object) -> List[Optional[List[str]]]:
    result = []
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_object.file.read())
        temp_file.seek(0)

    with pdfplumber.open(temp_file.name) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page_result = []
            tables = page.extract_tables()
            if not tables:
                page_result.append("No tables found.")
            else:
                for table_num, table in enumerate(tables):
                    if table:
                        table_columns = [table[0]]  # First row to show column names
                        page_result.extend(table_columns)
                    else:
                        page_result.append(f"Table {table_num + 1} is empty.")
            result.append(page_result)
    return result


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
