from fastapi import UploadFile

from repository.source_repository import source_repository
from service.chat_pdf_service import ChatPdfService


def upload_file(fileObject: UploadFile) -> str:
    file_service = ChatPdfService
    source_id = file_service.upload_file(fileObject.file)
    return source_id
