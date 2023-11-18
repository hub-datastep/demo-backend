from fastapi import HTTPException

from dto.message_dto import MessageOutDto, MessageCreateDto, FavoriteMessageDto, CreateFavoriteMessageDto
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
    
    @classmethod
    def get_favorites_list(cls, user_id: str) -> list[FavoriteMessageDto]:
        response = supabase\
            .table("favorite")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()
        return [FavoriteMessageDto(**favorite_question) for favorite_question in response.data]
    
    @classmethod
    def add_favorite_message(cls, body: CreateFavoriteMessageDto):
        supabase\
            .table("favorite")\
            .insert(body.model_dump())\
            .execute()           

message_repository = MessageRepository()
