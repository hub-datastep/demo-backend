from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model.auth_model import get_current_user
from repository import prompt_repository
from scheme.prompt_scheme import PromptRead, PromptCreate, PromptUpdate
from scheme.user_scheme import UserRead

router = APIRouter()


@router.get("", response_model=PromptRead)
@version(1)
def get_prompt_by_tenant_id(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user_tenant_id = current_user.tenants[0].id
    return prompt_repository.get_prompt_by_tenant_id(session, user_tenant_id)


@router.get("/tables")
@version(1)
def get_tenant_tables(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user_tenant_id = current_user.tenants[0].id
    return prompt_repository.get_tenant_tables(session, user_tenant_id)


@router.post("", response_model=PromptRead)
@version(1)
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
def update_prompt(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    prompt_id: int,
    new_prompt: PromptUpdate,
):
    return prompt_repository.update_prompt(session, prompt_id, new_prompt)
