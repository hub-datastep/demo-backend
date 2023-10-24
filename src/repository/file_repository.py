from dto.file_dto import FileDto, FileOutDto
from infra.supabase import supabase


def get_all_filenames_ru(chat_id: int) -> list[FileOutDto]:
    (_, filenames), _ = supabase\
        .table("file")\
        .select("*") \
        .eq("status", "active") \
        .in_("chat_id", [chat_id, 666666])\
        .order("id", desc=False)\
        .execute()
    return [FileOutDto(**filename) for filename in filenames]


def get_file_by_task_id(task_id: int) -> FileOutDto:
    (_, filename), _ = supabase \
        .table("file") \
        .select("*") \
        .eq("file_upload_task_id", task_id) \
        .execute()
    return FileOutDto(**filename[0])


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
        .eq("name_ru", name_ru) \
        .neq("status", "deleted") \
        .execute()

    if len(files) == 0:
        return False
    return True


def is_file_exists_in_other_chats(chat_id: int, name_ru: str) -> bool:
    (_, files), _ = supabase\
        .table("file")\
        .select("*")\
        .neq("chat_id", chat_id)\
        .neq("status", "deleted")\
        .eq("name_ru", name_ru)\
        .execute()
    if len(files) == 0:
        return False
    return True


def update(match: dict, update: dict):
    supabase\
        .table("file")\
        .update(update)\
        .match(match)\
        .execute()


if __name__ == "__main__":
    get_all_filenames_ru(18)
