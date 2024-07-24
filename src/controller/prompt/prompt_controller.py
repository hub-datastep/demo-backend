from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from middleware.role_middleware import admins_only
from model.auth.auth_model import get_current_user
from repository.prompt import prompt_repository
from scheme.prompt.prompt_scheme import PromptRead, PromptCreate, PromptUpdate
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("/active", response_model=PromptRead | None)
@version(1)
@admins_only
def get_active_tenant_prompt(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user_tenant_id = current_user.tenant_id
    return prompt_repository.get_active_tenant_prompt(session, user_tenant_id)


@router.get("/tables")
@version(1)
@admins_only
def get_tenant_tables(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user_tenant_id = current_user.tenant_id
    return prompt_repository.get_tenant_tables(session, user_tenant_id)


@router.post("", response_model=PromptRead)
@version(1)
@admins_only
def create_prompt(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    prompt: PromptCreate,
):
    """
    """
    return prompt_repository.create_prompt(session, prompt)


@router.put("/{prompt_id}", response_model=PromptRead)
@version(1)
@admins_only
def update_prompt(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    prompt_id: int,
    new_prompt: PromptUpdate,
):
    return prompt_repository.update_prompt(session, prompt_id, new_prompt)
