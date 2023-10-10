from fastapi import UploadFile

from dto.file_dto import FileDto, FileOutDto
from repository import file_repository
from service.supastorage_service import upload_file_to_supastorage


def save_file(chat_id: int, fileObject: UploadFile) -> FileOutDto:
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
