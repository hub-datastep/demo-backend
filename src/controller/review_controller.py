from fastapi import APIRouter, HTTPException

from dto.review_dto import ReviewOutDto, ReviewCreateDto
from repository.review_repository import review_repository

router = APIRouter(
    prefix="/review",
    tags=["review"],
)


@router.post("/", response_model=ReviewOutDto)
async def update_or_create_review(body: ReviewCreateDto):
    try:
        review_repository.get_by_message_id(body)
        review_repository.update(body)
    except HTTPException as e:
        if e.status_code == 404:
            review_repository.create(body)
        else:
            raise e
