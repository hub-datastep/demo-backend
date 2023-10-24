from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.mark_dto import MarkCreateDto, MarkOutDto
from dto.user_dto import UserDto
from repository.mark_repository import mark_repository
from service.auth_service import AuthService

router = APIRouter(
    prefix="/mark",
    tags=["mark"],
)


@router.post("", response_model=MarkOutDto)
@version(1)
def create_mark(body: MarkCreateDto, current_user: UserDto = Depends(AuthService.get_current_user)):
    return mark_repository.create(body)

