import logging

from fastapi import UploadFile

from dto.source_dto import SourceCreateDto, SourceDto
from repository.source_repository import source_repository
from service.chat_pdf_service import ChatPdfService


def save_source(chat_id: int, fileObject: UploadFile) -> SourceDto:
    source_service = ChatPdfService

    source_id = source_service.upload_file(fileObject.file)
    source = source_repository.save_source(
        SourceCreateDto(
            source_id=source_id,
            chat_id=chat_id,
            file_name=fileObject.filename,
        )
    )

    return source
