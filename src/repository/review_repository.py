from dto.review_dto import ReviewOutDto, ReviewCreateDto
from infra.supabase import supabase
from repository.message_repository import message_repository


class ReviewRepository:
    @classmethod
    def get_by_message_id(cls, message_id: int) -> list[ReviewOutDto]:
        message = message_repository.fetch_by_id(message_id)
        return message.review

    @classmethod
    def create(cls, body: ReviewCreateDto) -> ReviewOutDto:
        (_, [review]), _ = supabase.table("review").insert(body.model_dump()).execute()
        return ReviewOutDto(**review)


review_repository = ReviewRepository()
