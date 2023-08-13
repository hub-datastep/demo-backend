from fastapi import APIRouter

from dto.mark_dto import MarkCreateDto, MarkOutDto
from repository.mark_repository import mark_repository

router = APIRouter(
    prefix="/mark",
    tags=["mark"],
)


@router.post("", response_model=MarkOutDto)
async def create_mark(body: MarkCreateDto):
    return mark_repository.create(body)

