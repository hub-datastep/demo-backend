from dto.file_dto import FileDto
from infra.supabase import supabase


def get_all_filenames_ru() -> list[FileDto]:
    (_, filenames), _ = supabase.table("file").select("*").execute()
    return [FileDto(**filename) for filename in filenames]
