import pathlib
import shutil

from fastapi import UploadFile, BackgroundTasks, HTTPException

from datastep.components import datastep_faiss, datastep_multivector
from dto.file_dto import FileDto, FileOutDto, StorageFileDto
from repository import file_repository
from service.supastorage_service import upload_file_to_supastorage, sanitize_filename, get_file_public_url, delete_file_from_supastorage
from storage3.utils import StorageException


async def save_file(chat_id: int, file_object: UploadFile, background_tasks: BackgroundTasks) -> FileOutDto:
    if file_repository.is_file_exists(chat_id, file_object.filename):
        raise HTTPException(
            status_code=409,
            detail="Файл с таким названием уже загружен"
        )

    try:
        storage_file: StorageFileDto = upload_file_to_supastorage(file_object)
    except StorageException as e:
        dict_, = e.args
        if dict_["error"] == "Duplicate":
            normal_filename = sanitize_filename(file_object.filename)
            full_file_url = get_file_public_url(normal_filename)

            file = file_repository.save_file(
                FileDto(
                    name_ru=file_object.filename,
                    name_en=normal_filename,
                    url=full_file_url,
                    chat_id=chat_id,
                    status="uploading"
                )
            )
            return file
        elif dict_["error"] == "Invalid Input":
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

    datastep_faiss.save_document(storage_file.filename, storage_file.fileUrl)
    background_tasks.add_task(datastep_multivector.save_document, file.id, storage_file.filename, storage_file.fileUrl)

    return file


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
