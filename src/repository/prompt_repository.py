from config.config import config
from dto.prompt_out_dto import PromptOutDto, PromptEditDto
from infra.supabase import supabase


class PromptRepository:
    @classmethod
    def fetch_by_id(cls, prompt_id: int) -> PromptOutDto:
        (_, [prompt]), _ = supabase.table("prompt").select("*").eq("id", prompt_id).execute()
        return PromptOutDto(**prompt)

    @classmethod
    def edit(cls, body: PromptEditDto) -> PromptOutDto:
        (_, [prompt]), _ = supabase.table("prompt").update(body.model_dump()).eq("id", config["prompt_id"]).execute()
        return PromptOutDto(**prompt)


prompt_repository = PromptRepository()
