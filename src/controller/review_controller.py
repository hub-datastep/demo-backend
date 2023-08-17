from fastapi import APIRouter
from fastapi_versioning import version

from dto.review_dto import ReviewOutDto, ReviewCreateDto
from repository.review_repository import review_repository

router = APIRouter(
    prefix="/review",
    tags=["review"],
)


@router.post("", response_model=ReviewOutDto)
@version(1)
async def create_review(body: ReviewCreateDto):
    return review_repository.create(body)
