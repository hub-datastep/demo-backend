from sqlmodel import Session, select

from scheme.message_scheme import MessageCreate, Message
from dto.message_dto import MessageOutDto, MessageCreateDto, FavoriteMessageDto, CreateFavoriteMessageDto
# from infra.supabase import supabase


def create_message(session: Session, message: MessageCreate) -> Message:
    message_db = Message.from_orm(message)
    session.add(message_db)
    session.commit()
    return message_db


def drop_all_messages_by_chat_id(session: Session, chat_id: int) -> list[Message]:
    statement = select(Message).where(Message.chat_id == chat_id)
    result = session.exec(statement)
    messages = result.all()

    for message in messages:
        message.is_deleted = True

    session.add(messages)
    session.commit()

    return list(messages)


def get_favorites_list(user_id: str) -> list[FavoriteMessageDto]:
    pass
    # response = supabase\
    #     .table("favorite")\
    #     .select("*")\
    #     .eq("user_id", user_id)\
    #     .execute()
    # return [FavoriteMessageDto(**favorite_question) for favorite_question in response.data]


def add_favorite_message(body: CreateFavoriteMessageDto):
    pass
    # supabase\
    #     .table("favorite")\
    #     .insert(body.model_dump())\
    #     .execute()


def remove_favorite_message(favorite_message_id: int):
    pass
    # supabase\
    #     .table("favorite")\
    #     .delete()\
    #     .eq("id", favorite_message_id)\
    #     .execute()
