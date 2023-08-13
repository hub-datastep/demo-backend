from dto.message_dto import MessageOutDto, MessageCreateDto
from infra.supabase import supabase


class MessageRepository:
    @classmethod
    def fetch_all_by_chat_id(cls, chat_id: int) -> list[MessageOutDto]:
        (_, messages), _ = supabase.table("message").select("*, review(*)").eq("chat_id", chat_id).execute()
        return [MessageOutDto(**message) for message in messages]

    @classmethod
    def create(cls, body: MessageCreateDto) -> MessageOutDto:
        (_, [message]), _ = supabase.table("message").insert(body.model_dump()).execute()
        return MessageOutDto(**message)


message_repository = MessageRepository()
