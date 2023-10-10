from fastapi import UploadFile

from repository import file_repository
from service.supastorage_service import upload_file_to_supastorage
from src.dto.file_dto import FileDto


def save_file(chat_id: int, fileObject: UploadFile) -> FileDto:
    storageFile = upload_file_to_supastorage(fileObject)

    file = file_repository.save_file(
        FileDto(
            name_ru=fileObject.filename,
            name_en=storageFile.filename,
            url=storageFile.fileUrl,
            chat_id=chat_id
        )
    )

    return file
