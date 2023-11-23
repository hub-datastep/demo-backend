from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from dto.prompt_dto import PromptDto, PromptEditDto
from dto.user_dto import UserDto
from infra.database import get_session
from repository import prompt_repository
from scheme.prompt_scheme import PromptRead, PromptCreate, PromptUpdate
from service.auth_service import AuthService

router = APIRouter(
    prefix="/prompt",
    tags=["prompt"],
)

@router.get("/{tenant_id}", response_model=PromptRead)
@version(1)
def get_prompt_by_tenant_id(*, session: Session = Depends(get_session), tenant_id: int):
    return prompt_repository.get_prompt_by_tenant_id(session, tenant_id)


@router.post("", response_model=PromptRead)
@version(1)
def create_prompt(*, session: Session = Depends(get_session), prompt: PromptCreate):
    return prompt_repository.create_prompt(session, prompt)


@router.put("", response_model=PromptRead)
@version(1)
def update_prompt(*, session: Session = Depends(get_session), prompt: PromptUpdate):
    return prompt_repository.update_prompt(session, prompt)
