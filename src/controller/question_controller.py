from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.user_dto import UserDto
from model import question_model
from service.auth_service import AuthService

router = APIRouter(
    prefix="/question",
    tags=["question"],
)


@router.get("/{limit}")
@version(1)
def get_template_questions(limit: int, current_user: UserDto = Depends(AuthService.get_current_user)):
    return question_model.get_random_questions(limit)
