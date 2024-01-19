from fastapi import HTTPException
from sqlmodel import Session
from sqlmodel import select

from scheme.prompt_scheme import PromptCreate, Prompt, PromptUpdate


def get_prompt_by_tenant_id(session: Session, tenant_id: int) -> Prompt:
    statement = select(Prompt).where(Prompt.tenant_id == tenant_id)
    result = session.exec(statement)
    prompt_db = result.one()
    return prompt_db


def create_prompt(session: Session, prompt: PromptCreate) -> Prompt:
    prompt_db = Prompt.from_orm(prompt)
    session.add(prompt_db)
    session.commit()
    return prompt_db


def update_prompt(session: Session, prompt_id: int, prompt: PromptUpdate) -> Prompt:
    prompt_db = session.get(Prompt, prompt_id)

    if prompt_db is None:
        raise HTTPException(status_code=404, detail=f"Prompt with prompt_id={prompt_id} is not found.")

    prompt_db.is_active = prompt.is_active
    prompt_db.prompt = prompt.prompt
    session.add(prompt_db)
    session.commit()

    return prompt_db


# class PromptRepository:
#     @classmethod
#     def fetch_tenant_id(cls, prompt_id: int) -> PromptDto:
#         (_, [prompt]), _ = supabase.table("prompt").select("*").eq("id", prompt_id).execute()
#         return PromptDto(**prompt)
#
#     @classmethod
#     # @log("Получение промпта")
#     def get_active_prompt_by_tenant_id(cls, tenant_id: int, table: str) -> PromptDto:
#         response = supabase\
#             .table("prompt")\
#             .select("*")\
#             .eq("tenant_id", tenant_id)\
#             .eq("table", table) \
#             .eq("is_active", True)\
#             .execute()
#
#         if len(response.data) == 0:
#             raise HTTPException(status_code=404, detail="Cannot found prompt for current user")
#
#         return PromptDto(**response.data[0])
#
#     @classmethod
#     def edit_by_id(cls, prompt_id: int, body: PromptEditDto) -> PromptDto:
#         (_, [prompt]), _ = supabase\
#             .table("prompt")\
#             .update(body.model_dump())\
#             .eq("id", prompt_id)\
#             .execute()
#         return PromptDto(**prompt)
#
#
# prompt_repository = PromptRepository()
