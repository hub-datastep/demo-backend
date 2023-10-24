from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.prompt_dto import PromptDto, PromptEditDto
from dto.user_dto import UserDto
from repository.prompt_repository import prompt_repository
from service.auth_service import AuthService

router = APIRouter(
    prefix="/prompt",
    tags=["prompt"],
)


@router.put("/{prompt_id}", response_model=PromptDto)
@version(1)
def edit_prompt(
    prompt_id: int,
    body: PromptEditDto,
    current_user: UserDto = Depends(AuthService.get_current_user)
):
    return prompt_repository.edit_by_id(prompt_id, body)
