from sqlmodel import Session

from scheme.review_scheme import Review, ReviewCreate


def create_review(session: Session, review: ReviewCreate) -> Review:
    review_db = Review.from_orm(review)
    session.add(review_db)
    session.commit()
    return review_db

# class ReviewRepository:
#     @classmethod
#     def get_by_message_id(cls, message_id: int) -> list[ReviewOutDto]:
#         message = message_repository.fetch_by_id(message_id)
#         return message.review
#
#     @classmethod
#     def create(cls, body: ReviewCreateDto) -> ReviewOutDto:
#         (_, [review]), _ = supabase.table("review").insert(body.model_dump()).execute()
#         return ReviewOutDto(**review)
#
#
# review_repository = ReviewRepository()
