from fastapi import HTTPException
from sqlmodel import Session, select

from scheme.prompt.prompt_scheme import PromptCreate, Prompt, PromptUpdate
from scheme.tenant.tenant_scheme import Tenant


def get_active_tenant_prompt(session: Session, tenant_id: int) -> Prompt | None:
    st = select(Prompt).where(Prompt.tenant_id == tenant_id).where(Prompt.is_active)
    prompt = session.exec(st).first()
    return prompt


def get_tenant_tables(session: Session, tenant_id: int) -> list[str]:
    statement = select(Prompt.table).distinct().where(Prompt.tenant_id == tenant_id)
    result = session.exec(statement)
    tenant_tables = result.all()

    return list(tenant_tables)


def create_prompt(session: Session, prompt: PromptCreate) -> Prompt:
    tenant_db = session.get(Tenant, prompt.tenant_id)

    prompt_db = Prompt.from_orm(prompt)
    prompt_db.tenant = tenant_db

    session.add(prompt_db)
    session.commit()
    return prompt_db


def update_prompt(session: Session, prompt_id: int, new_prompt: PromptUpdate) -> Prompt:
    prompt_db = session.get(Prompt, prompt_id)

    if prompt_db is None:
        raise HTTPException(
            status_code=404,
            detail=f"Prompt with ID {prompt_id} is not found.",
        )

    prompt_db.is_active = new_prompt.is_active
    prompt_db.prompt = new_prompt.prompt
    session.add(prompt_db)
    session.commit()
    session.refresh(prompt_db)

    return prompt_db
