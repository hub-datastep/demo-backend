from dto.mark_dto import MarkOutDto, MarkCreateDto
from infra.supabase import supabase
from repository.message_repository import message_repository


class MarkRepository:
    @classmethod
    def fetch_by_message_id(cls, message_id: int) -> MarkOutDto:
        message = message_repository.fetch_by_id(message_id)
        return message.mark

    @classmethod
    def create(cls, body: MarkCreateDto) -> MarkOutDto:
        (_, marks), _ = supabase.table("mark").select("*").eq("message_id", body.message_id).execute()

        if len(marks) == 0:
            (_, [mark]), _ = supabase.table("mark").insert(body.model_dump()).execute()
            return mark

        (_, [mark]), _ = supabase.table("mark").update(body.model_dump()).eq("message_id", body.message_id).execute()
        return MarkOutDto(**mark)


mark_repository = MarkRepository()
