from fastapi import APIRouter, Depends
from fastapi_versioning import version

from config.config import config
from dto.prompt_out_dto import PromptOutDto, PromptEditDto
from dto.user_dto import UserDto
from repository.prompt_repository import prompt_repository
from service.auth_service import AuthService

router = APIRouter(
    prefix="/prompt",
    tags=["prompt"],
)


@router.get("", response_model=PromptOutDto)
@version(1)
async def get_prompt(current_user: UserDto = Depends(AuthService.get_current_user)):
    return prompt_repository.fetch_by_id(config["prompt_id"])


@router.put("", response_model=PromptOutDto)
@version(1)
async def edit_prompt(body: PromptEditDto, current_user: UserDto = Depends(AuthService.get_current_user)):
    return prompt_repository.edit(body)
