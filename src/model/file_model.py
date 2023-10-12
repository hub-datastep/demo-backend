from fastapi import HTTPException

from fastapi import UploadFile

from datastep.components import datastep_faiss
from dto.file_dto import FileDto, FileOutDto, StorageFileDto
from repository import file_repository
from service.supastorage_service import upload_file_to_supastorage
from storage3.utils import StorageException


def save_file(chat_id: int, file_object: UploadFile) -> FileOutDto:
    try:
        storage_file: StorageFileDto = upload_file_to_supastorage(file_object)
    except StorageException as e:
        dict_, = e.args
        if dict_["error"] == "Duplicate":
            raise HTTPException(status_code=409, detail="Файл с таким названием уже загружен")
        elif dict_["error"] == "Invalid Input":
            raise HTTPException(status_code=400, detail="В названии файла есть недопустимые символы")
        raise e

    datastep_faiss.save_document(storage_file.filename, storage_file.fileUrl)

    file = file_repository.save_file(
        FileDto(
            name_ru=file_object.filename,
            name_en=storage_file.filename,
            url=storage_file.fileUrl,
            chat_id=chat_id
        )
    )

    return file
