from dto.file_dto import FileDto, FileOutDto
from infra.supabase import supabase


def get_all_filenames_ru(chat_id: int) -> list[FileOutDto]:
    (_, filenames), _ = supabase\
        .table("file")\
        .select("*")\
        .in_("chat_id", [chat_id, 666666])\
        .order("id", desc=False)\
        .execute()
    return [FileOutDto(**filename) for filename in filenames]


def save_file(body: FileDto) -> FileOutDto:
    (_, [file]), _ = supabase\
        .table("file")\
        .insert(body.model_dump())\
        .execute()
    return FileOutDto(**file)


def is_file_exists(chat_id: int, name_ru: str) -> bool:
    (_, files), _ = supabase\
        .table("file")\
        .select("*")\
        .eq("chat_id", chat_id)\
        .eq("name_ru", name_ru)\
        .execute()

    if (len(files) == 0):
        return False
    return True
