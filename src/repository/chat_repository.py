from sqlmodel import Session, select

from scheme.chat_scheme import ChatCreate, Chat


def get_chat_by_user_id(session: Session, user_id: int) -> Chat | None:
    st = select(Chat).where(Chat.user_id == user_id)
    chat_db = session.exec(st).first()
    return chat_db


def create_chat(session: Session, chat: ChatCreate) -> Chat:
    chat_db = Chat.from_orm(chat)
    session.add(chat_db)
    session.commit()
    session.refresh(chat_db)
    return chat_db
