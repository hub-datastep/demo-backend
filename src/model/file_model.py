from fastapi import UploadFile

from datastep.components import datastep_faiss
from dto.file_dto import FileDto, FileOutDto, StorageFileDto
from repository import file_repository
from service.supastorage_service import upload_file_to_supastorage


def save_file(chat_id: int, fileObject: UploadFile) -> FileOutDto:
    storageFile: StorageFileDto = upload_file_to_supastorage(fileObject)

    datastep_faiss.save_document(storageFile.filename, storageFile.fileUrl)

    file = file_repository.save_file(
        FileDto(
            name_ru=fileObject.filename,
            name_en=storageFile.filename,
            url=storageFile.fileUrl,
            chat_id=chat_id
        )
    )

    return file
