from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.question_dto import QuestionGetDto
from dto.user_dto import UserDto
from model import question_model
from service.auth_service import AuthService

router = APIRouter(
    prefix="/question",
    tags=["question"],
)


@router.post("/")
@version(1)
async def get_template_questions(body: QuestionGetDto, current_user: UserDto = Depends(AuthService.get_current_user)):
    return question_model.get_random_questions(body.tables, body.limit)
