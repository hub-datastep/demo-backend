from typing import Generator

from dto.query_dto import QueryDto
from repository.message_repository import message_repository
from service.chatpdf_service import ChatPdfService


def include_chat_history(messages: list[dict], chat_id: int) -> None:
    messages_as_dtos = message_repository.fetch_all_by_chat_id(chat_id)

    for message in messages_as_dtos:
        if message.query not in (None, ""):
            messages.append(ChatPdfService.create_user_message(message.query))
        elif message.answer not in (None, ""):
            messages.append(ChatPdfService.create_assistant_message(message.query))


def get_prediction(body: QueryDto) -> Generator:
    messages = []

    # include_chat_history(messages, body.chat_id)
    messages.append(ChatPdfService.create_user_message(body.query))

    return ChatPdfService.run(messages, body.fileObject.file)
