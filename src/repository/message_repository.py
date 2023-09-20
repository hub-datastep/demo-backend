from fastapi import HTTPException

from dto.message_dto import MessageOutDto, MessageCreateDto
from infra.supabase import supabase


class MessageRepository:
    @classmethod
    def fetch_by_id(cls, message_id: int) -> MessageOutDto:
        (_, messages), _ = supabase\
            .table("message")\
            .select("*, review(*), mark(*)")\
            .eq("id", message_id)\
            .execute()

        if len(messages) == 0:
            raise HTTPException(status_code=404, detail=f"Message with id={message_id} has no reviews.")

        return MessageOutDto(**(messages[0]))

    @classmethod
    def fetch_all_by_chat_id(cls, chat_id: int) -> list[MessageOutDto]:
        (_, messages), _ = supabase\
            .table("message")\
            .select("*, review(*)")\
            .eq("chat_id", chat_id)\
            .neq("is_deleted", True)\
            .execute()
        return [MessageOutDto(**message) for message in messages]

    @classmethod
    def create(cls, body: MessageCreateDto) -> MessageOutDto:
        (_, [message]), _ = supabase.table("message").insert(body.model_dump()).execute()
        return MessageOutDto(**message)
    
    @classmethod
    def clear(cls, chat_id: int):
        (_, messages), _ = supabase\
            .table("message")\
            .update({ "is_deleted": True })\
            .eq("chat_id", chat_id)\
            .execute()
        return [MessageOutDto(**message) for message in messages]


message_repository = MessageRepository()
