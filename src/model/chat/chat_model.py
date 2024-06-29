from fastapi import HTTPException
from sqlmodel import Session

from repository import chat_repository
from scheme.chat.chat_scheme import Chat


def get_chat_by_user_id(session: Session, user_id: int, mode_id: int) -> Chat | None:
    chat = chat_repository.get_chat_by_user_id(session, user_id, mode_id)

    if not chat:
        raise HTTPException(
            status_code=404,
            detail=f"Chat with user_id {user_id} not found.",
        )

    return chat
