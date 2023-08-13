from fastapi import HTTPException

from dto.review_dto import ReviewOutDto, ReviewCreateDto
from infra.supabase import supabase


class ReviewRepository:
    @classmethod
    def get_by_message_id(cls, message_id: int) -> ReviewOutDto:
        (_, reviews), _ = supabase.table("review").select("*").eq("message_id", message_id).execute()

        if len(reviews) == 0:
            raise HTTPException(status_code=404, detail=f"Message with id={message_id} has no reviews.")

        return ReviewOutDto(**(reviews[0]))

    @classmethod
    def create(cls, body: ReviewCreateDto) -> ReviewOutDto:
        (_, [review]), _ = supabase.table("review").insert(body.model_dump()).execute()
        return ReviewOutDto(**review)

    @classmethod
    def update(cls, body: ReviewCreateDto) -> ReviewOutDto:
        (_, [review]), _ = supabase\
            .table("review")\
            .update(body.model_dump())\
            .eq("message_id", body.message_id)\
            .execute()
        return ReviewOutDto(**review)


review_repository = ReviewRepository()
