from fastapi import HTTPException
from sqlmodel import Session, select

# from infra.supabase import supabase
from scheme.chat_scheme import ChatCreate, Chat


def create_chat(session: Session, chat: ChatCreate) -> Chat:
    chat_db = Chat.from_orm(chat)
    session.add(chat_db)
    session.commit()
    return chat_db


def get_chat_by_user_id(session: Session, user_id: int) -> Chat:
    statement = select(Chat).where(Chat.user_id == user_id)
    result = session.exec(statement)
    chat_db = result.first()
    if not chat_db:
        raise HTTPException(status_code=404, detail="No chat found")
    return chat_db


# class ChatRepository:
#     @classmethod
#     def create(cls, body: ChatCreateDto) -> ChatOutDto:
#         (_, [chat]), _ = supabase.table("chat").insert(body.model_dump()).execute()
#         return ChatOutDto(**chat)
#
#     @classmethod
#     def fetch_by_user_id(cls, user_id: str) -> ChatOutDto:
#         (_, chats), _ = supabase\
#             .table("chat")\
#             .select("*, message(*, review(*), mark(*))")\
#             .eq("user_id", user_id)\
#             .neq("message.is_deleted", True)\
#             .execute()
#
#         if len(chats) == 0:
#             raise HTTPException(status_code=404, detail=f"User with user_id={user_id} does not have any chats.")
#
#         return ChatOutDto(**(chats[0]))
#
#
# chat_repository = ChatRepository()
