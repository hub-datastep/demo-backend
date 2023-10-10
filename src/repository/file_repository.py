from dto.file_dto import FileDto, FileOutDto
from infra.supabase import supabase


def get_all_filenames_ru() -> list[FileDto]:
    (_, filenames), _ = supabase.table("file").select("*").execute()
    return [FileDto(**filename) for filename in filenames]


def save_file(body: FileDto) -> FileOutDto:
    (_, [file]), _ = supabase\
        .table("file")\
        .insert(body.model_dump())\
        .execute()
    return FileDto(**file)
