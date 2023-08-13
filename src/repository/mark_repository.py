from dto.mark_dto import MarkOutDto
from dto.message_dto import MessageOutDto
from dto.review_dto import ReviewOutDto, ReviewCreateDto
from infra.supabase import supabase
from repository.message_repository import message_repository


class MarkRepository:
    @classmethod
    def fetch_by_message_id(cls, message_id: int) -> MarkOutDto:
        message = message_repository.fetch_by_id(message_id)
        return message.mark

    @classmethod
    def create(cls, body: ReviewCreateDto) -> MarkOutDto:
        (_, [mark]), _ = supabase.table("mark").insert(body.model_dump()).execute()
        return MarkOutDto(**mark)


mark_repository = MarkRepository()
