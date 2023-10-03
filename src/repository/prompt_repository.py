from config.config import config
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
        # TODO: при первом создании тенанта, промта явно не будет, если его не будет, то будет вылетать ошибка, надо будет это предусмотреть
        # TODO case 1: сделать для промта дефолтное значение - пустую строку (супабейз такое умеет)
        # TODO case 2: сделать дефолтное значение для промтов в супабейзе
        # TODO case 3: выдавать exception что промта нет
        return PromptOutDto(**prompt)

    @classmethod
    def edit(cls, body: PromptEditDto) -> PromptOutDto:
        (_, [prompt]), _ = supabase.table("prompt").update(body.model_dump()).eq("id", config["prompt_id"]).execute()
        return PromptOutDto(**prompt)


prompt_repository = PromptRepository()
