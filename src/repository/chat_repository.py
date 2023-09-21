from fastapi import HTTPException

from dto.chat_dto import ChatCreateDto, ChatOutDto
from infra.supabase import supabase


class ChatRepository:
    @classmethod
    def create(cls, body: ChatCreateDto) -> ChatOutDto:
        (_, [chat]), _ = supabase.table("chat").insert(body.model_dump()).execute()
        return ChatOutDto(**chat)

    @classmethod
    def fetch_by_user_id(cls, user_id: str) -> ChatOutDto:
        (_, chats), _ = supabase\
            .table("chat")\
            .select("*, message(*, review(*), mark(*))")\
            .eq("user_id", user_id)\
            .execute()

        if len(chats) == 0:
            raise HTTPException(status_code=404, detail=f"User with user_id={user_id} does not have any chats.")

        return ChatOutDto(**(chats[0]))


chat_repository = ChatRepository()
