from dto.source_dto import SourceCreateDto, SourceDto
from infra.supabase import supabase


class SourceRepository:
    @classmethod
    def get_last_source(cls, chat_id: int) -> SourceDto:
        (_, sources), _ = supabase\
            .table("source")\
            .select("*")\
            .eq("chat_id", chat_id)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()

        if len(sources) == 0:
            return None

        return SourceDto(**(sources[0]))

    @classmethod
    def get_all_sources(cls, chat_id: int) -> list[SourceDto]:
        (_, sourcesList), _ = supabase\
            .table("source")\
            .select("*")\
            .eq("chat_id", chat_id)\
            .execute()
        return [SourceDto(**sourceItem) for sourceItem in sourcesList]

    @classmethod
    def save_source(cls, body: SourceCreateDto) -> SourceDto:
        (_, [source]), _ = supabase\
            .table("source")\
            .insert(body.model_dump())\
            .execute()
        return SourceDto(**source)


source_repository = SourceRepository()
