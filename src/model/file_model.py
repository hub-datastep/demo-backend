from fastapi import HTTPException

from fastapi import UploadFile

from datastep.components import datastep_faiss
from dto.file_dto import FileDto, FileOutDto, StorageFileDto
from repository import file_repository
from service.supastorage_service import upload_file_to_supastorage, sanitize_filename, get_file_public_url, delete_file_from_supastorage
from storage3.utils import StorageException


def save_file(chat_id: int, file_object: UploadFile) -> FileOutDto:
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
                    chat_id=chat_id
                )
            )
            return file
        elif dict_["error"] == "Invalid Input":
            raise HTTPException(
                status_code=400,
                detail="В названии файла есть недопустимые символы"
            )
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

def delete_file(body: FileOutDto):
    file_repository.delete_file(body.id)
    if not file_repository.is_file_exists_in_other_chats(body.chat_id, body.name_ru):
        delete_file_from_supastorage(body.name_en)
        datastep_faiss.delete_document(body.name_en)
    
        
