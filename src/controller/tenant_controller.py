from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.prompt_dto import PromptDto
from dto.user_dto import UserDto
from repository.prompt_repository import prompt_repository
from service.auth_service import AuthService

router = APIRouter(
    prefix="/tenant",
    tags=["tenant"],
)


@router.get("/{tenant_id}/prompt/active", response_model=PromptDto)
@version(1)
def get_active_prompt(tenant_id: int, current_user: UserDto = Depends(AuthService.get_current_user)):
    return prompt_repository.get_active_prompt_by_tenant_id(tenant_id)
