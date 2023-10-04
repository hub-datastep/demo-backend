from config.config import config
from datastep.datastep_chains.datastep_sql_chain import datastep_sql_chain_template
from dto.prompt_out_dto import PromptEditDto, PromptOutDto
from infra.supabase import supabase


class PromptRepository:
    @classmethod
    def fetch_by_id(cls, prompt_id: int) -> PromptOutDto:
        (_, [prompt]), _ = supabase.table("prompt").select("*").eq("id", prompt_id).execute()
        return PromptOutDto(**prompt)

    @classmethod
    def get_active_prompt_by_tenant_id(cls, tenant_id: int) -> PromptOutDto:
        (_, [prompt]), _ = supabase\
            .table("prompt")\
            .select("*")\
            .eq("tenant_id", tenant_id)\
            .eq("is_active", True)\
            .execute()

        if prompt == None:
            return datastep_sql_chain_template

        return PromptOutDto(**prompt)

    @classmethod
    def edit(cls, body: PromptEditDto) -> PromptOutDto:
        (_, [prompt]), _ = supabase.table("prompt").update(body.model_dump()).eq("id", config["prompt_id"]).execute()
        return PromptOutDto(**prompt)


prompt_repository = PromptRepository()
