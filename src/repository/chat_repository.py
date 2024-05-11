from sqlmodel import Session, select

from scheme.chat_scheme import ChatCreate, Chat


def get_chat_by_user_id(session: Session, user_id: int, mode_id: int) -> Chat | None:
    st = select(Chat).where(Chat.user_id == user_id).where(Chat.mode_id == mode_id)
    chat = session.exec(st).first()
    return chat


def create_chat(session: Session, chat: ChatCreate) -> Chat:
    new_chat = Chat.from_orm(chat)
    session.add(new_chat)
    session.commit()
    session.refresh(new_chat)
    return new_chat
