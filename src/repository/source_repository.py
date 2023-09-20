from dto.source_dto import SourceCreateDto, SourceOutDto
from infra.supabase import supabase


class SourceRepository:
    @classmethod
    def get_last_source(cls, chat_id: int) -> SourceOutDto:
        (_, sources), _ = supabase\
            .table("source")\
            .select("*")\
            .eq("chat_id", chat_id)\
            .order("id")\
            .limit(1)\
            .execute()

        if len(sources) == 0:
            return None

        return SourceOutDto(**(sources[0]))

    @classmethod
    def get_all_sources(cls, chat_id: int) -> list[SourceOutDto]:
        (_, sourcesList), _ = supabase\
            .table("source")\
            .select("*")\
            .eq("chat_id", chat_id)\
            .execute()
        return [SourceOutDto(**sourceItem) for sourceItem in sourcesList]

    @classmethod
    def save_source(cls, body: SourceCreateDto) -> SourceOutDto:
        (_, [source]), _ = supabase\
            .table("source")\
            .insert(body.model_dump())\
            .execute()
        return SourceOutDto(**source)


source_repository = SourceRepository()
source_repository = SourceRepository()
