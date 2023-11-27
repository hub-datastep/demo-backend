import os
import pathlib
import shutil

from fastapi import UploadFile, HTTPException
from rq import Queue, get_current_job
from rq.job import Job
from redis import Redis

from datastep.components import datastep_faiss, datastep_multivector
from dto.file_dto import FileDto, StorageFileDto, FileOutDto
from dto.user_dto import UserDto
from repository import file_repository
from service import supastorage_service
from service.supastorage_service import delete_file_from_supastorage
from storage3.utils import StorageException


def _save_file(file: FileOutDto, storage_file):
    try:
        job = get_current_job()
        job.meta["file_id"] = file.id
        job.save_meta()

        datastep_faiss.save_document(storage_file.filename, storage_file.fileUrl)
        datastep_multivector.save_document(file, storage_file.filename, storage_file.fileUrl)
    except Exception as e:
        delete_file(file)
        raise e


def save_file(chat_id: int, file_object: UploadFile, current_user: UserDto) -> Job:
    # Если файл есть в частной библиотеке или в общей библиотеке тенанта, то он уже отображается пользователю

    is_in_mutual_files \
        = len(file_repository.get_mutual_file_by_filename_ru(current_user.tenant_id, file_object.filename)) != 0

    is_in_personal_files \
        = len(file_repository.get_personal_file_by_filename_ru(chat_id, file_object.filename)) != 0

    if is_in_mutual_files or is_in_personal_files:
        raise HTTPException(
            status_code=409,
            detail="Файл с таким названием уже загружен"
        )

    try:
        storage_file: StorageFileDto = supastorage_service.upload_or_get_file(file_object)
    except StorageException as e:
        dict_, = e.args
        if dict_["error"] == "Invalid Input":
            raise HTTPException(
                status_code=400,
                detail="В названии файла есть недопустимые символы"
            )
        raise e

    file = file_repository.save_file(
        FileDto(
            name_ru=file_object.filename,
            name_en=storage_file.filename,
            url=storage_file.fileUrl,
            chat_id=chat_id,
            status="uploading"
        )
    )

    redis = Redis("redis")
    q = Queue("document", connection=redis)
    job = q.enqueue(_save_file, file, storage_file, result_ttl=86400, job_timeout="60m")
    job.meta["user_id"] = current_user.id
    job.save_meta()
    return job


def get_store_file_path(source_id: str) -> str:
    return f"{pathlib.Path(__file__).parent.resolve()}/../../data/{source_id}"


def delete_local_store(filename):
    try:
        store_file_path = get_store_file_path(filename)
        shutil.rmtree(store_file_path)
    except FileNotFoundError:
        pass


def delete_file(body: FileDto):
    file_repository.update({"id": body.id}, {"status": "deleted"})
    if not file_repository.is_file_exists_in_other_chats(body.chat_id, body.name_ru):
        delete_file_from_supastorage(body.name_en)
        delete_local_store(body.name_en)
