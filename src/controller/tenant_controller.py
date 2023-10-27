from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.prompt_dto import PromptDto
from dto.user_dto import UserDto
from repository.prompt_repository import prompt_repository
from service.auth_service import AuthService
from model.tenant_model import create_tenant_with_user_id

router = APIRouter(
    prefix="/tenant",
    tags=["tenant"],
)


@router.get("/{tenant_id}/prompt/active", response_model=PromptDto)
@version(1)
def get_active_prompt(tenant_id: int, current_user: UserDto = Depends(AuthService.get_current_user)):
    return prompt_repository.get_active_prompt_by_tenant_id(tenant_id, "платежи")

@router.post("/{user_id}")
@version(1)
def create_tenant(user_id: str):
    return create_tenant_with_user_id(user_id)
