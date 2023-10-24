from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.review_dto import ReviewOutDto, ReviewCreateDto
from dto.user_dto import UserDto
from repository.review_repository import review_repository
from service.auth_service import AuthService

router = APIRouter(
    prefix="/review",
    tags=["review"],
)


@router.post("", response_model=ReviewOutDto)
@version(1)
def create_review(body: ReviewCreateDto, current_user: UserDto = Depends(AuthService.get_current_user)):
    return review_repository.create(body)
