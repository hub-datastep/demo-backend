from sqlmodel import Session, select

from scheme.message_scheme import MessageCreate, Message


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



# class MessageRepository:
#     @classmethod
#     def fetch_by_id(cls, message_id: int) -> MessageOutDto:
#         (_, messages), _ = supabase\
#             .table("message")\
#             .select("*, review(*), mark(*)")\
#             .eq("id", message_id)\
#             .execute()
#
#         if len(messages) == 0:
#             raise HTTPException(status_code=404, detail=f"Message with id={message_id} has no reviews.")
#
#         return MessageOutDto(**(messages[0]))
#
#     @classmethod
#     def fetch_all_by_chat_id(cls, chat_id: int) -> list[MessageOutDto]:
#         (_, messages), _ = supabase\
#             .table("message")\
#             .select("*, review(*)")\
#             .eq("chat_id", chat_id)\
#             .neq("is_deleted", True)\
#             .execute()
#         return [MessageOutDto(**message) for message in messages]
#
#     @classmethod
#     def create(cls, body: MessageCreateDto) -> MessageOutDto:
#         (_, [message]), _ = supabase.table("message").insert(body.model_dump()).execute()
#         return MessageOutDto(**message)
#
#     @classmethod
#     def clear(cls, chat_id: int):
#         (_, messages), _ = supabase\
#             .table("message")\
#             .update({ "is_deleted": True })\
#             .eq("chat_id", chat_id)\
#             .execute()
#         return [MessageOutDto(**message) for message in messages]
#
#
# message_repository = MessageRepository()
