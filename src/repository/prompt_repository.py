from fastapi import HTTPException

from dto.prompt_dto import PromptEditDto, PromptDto
from infra.supabase import supabase
from util.logger import log


class PromptRepository:
    @classmethod
    def fetch_tenant_id(cls, prompt_id: int) -> PromptDto:
        (_, [prompt]), _ = supabase.table("prompt").select("*").eq("id", prompt_id).execute()
        return PromptDto(**prompt)

    @classmethod
    @log("Получение промпта")
    def get_active_prompt_by_tenant_id(cls, tenant_id: int, table: str) -> PromptDto:
        response = supabase\
            .table("prompt")\
            .select("*")\
            .eq("tenant_id", tenant_id)\
            .eq("table", table) \
            .eq("is_active", True)\
            .execute()

        if len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Cannot found prompt for current user")

        return PromptDto(**response.data[0])

    @classmethod
    def edit_by_id(cls, prompt_id: int, body: PromptEditDto) -> PromptDto:
        (_, [prompt]), _ = supabase\
            .table("prompt")\
            .update(body.model_dump())\
            .eq("id", prompt_id)\
            .execute()
        return PromptDto(**prompt)


prompt_repository = PromptRepository()
