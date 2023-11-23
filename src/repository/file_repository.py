# from dto.file_dto import FileDto, FileOutDto
#
#
# def get_all_filenames_ru(chat_id: int, tenant_id: int) -> list[FileOutDto]:
#     (_, mutual_files_ids), _ = supabase\
#         .table("file_tenant")\
#         .select("file_id")\
#         .eq("tenant_id", tenant_id)\
#         .execute()
#     mutual_files_ids = [entry["file_id"] for entry in mutual_files_ids]
#
#     (_, mutual_files), _ = supabase \
#         .table("file") \
#         .select("*") \
#         .in_("id", mutual_files_ids) \
#         .eq("status", "active") \
#         .execute()
#
#     (_, personal_files), _ = supabase\
#         .table("file") \
#         .select("*") \
#         .eq("chat_id", chat_id) \
#         .not_.in_("id", mutual_files_ids) \
#         .eq("status", "active") \
#         .execute()
#
#     all_files = [*mutual_files, *personal_files]
#     return [FileOutDto(**filename) for filename in all_files]
#
#
# def get_mutual_file_by_filename_ru(tenant_id: int, filename_ru: str) -> list[FileOutDto]:
#     (_, files), _ = supabase \
#         .table("file") \
#         .select("*") \
#         .eq("status", "active") \
#         .eq("name_ru", filename_ru) \
#         .execute()
#
#     if len(files) == 0:
#         return []
#
#     (_, mutual_files), _ = supabase \
#         .table("file_tenant") \
#         .select("*") \
#         .eq("tenant_id", tenant_id) \
#         .eq("file_id", files[0]["id"]) \
#         .execute()
#
#     return [FileOutDto(**file) for file in mutual_files]
#
#
# def get_personal_file_by_filename_ru(chat_id: int, filename_ru: str) -> list[FileOutDto]:
#     (_, files), _ = supabase\
#         .table("file")\
#         .select("*")\
#         .eq("status", "active")\
#         .eq("name_ru", filename_ru)\
#         .eq("chat_id", chat_id)\
#         .execute()
#     return [FileOutDto(**file) for file in files]
#
#
# def get_file_by_task_id(task_id: int) -> FileOutDto:
#     (_, filename), _ = supabase \
#         .table("file") \
#         .select("*") \
#         .eq("file_upload_task_id", task_id) \
#         .execute()
#     return FileOutDto(**filename[0])
#
#
# def get_file_by_id(file_id: int) -> FileOutDto:
#     (_, filename), _ = supabase \
#         .table("file") \
#         .select("*") \
#         .eq("id", file_id) \
#         .neq("status", "deleted") \
#         .execute()
#     return FileOutDto(**filename[0])
#
#
# def save_file(body: FileDto) -> FileOutDto:
#     (_, [file]), _ = supabase\
#         .table("file")\
#         .insert(body.model_dump())\
#         .execute()
#     return FileOutDto(**file)
#
#
# def is_file_exists(chat_id: int, name_ru: str) -> bool:
#     (_, files), _ = supabase\
#         .table("file")\
#         .select("*")\
#         .eq("chat_id", chat_id)\
#         .eq("name_ru", name_ru) \
#         .neq("status", "deleted") \
#         .execute()
#
#     if len(files) == 0:
#         return False
#     return True
#
#
# def is_file_exists_in_other_chats(chat_id: int, name_ru: str) -> bool:
#     (_, files), _ = supabase\
#         .table("file")\
#         .select("*")\
#         .neq("chat_id", chat_id)\
#         .neq("status", "deleted")\
#         .eq("name_ru", name_ru)\
#         .execute()
#     if len(files) == 0:
#         return False
#     return True
#
#
# def update(match: dict, update: dict):
#     supabase\
#         .table("file")\
#         .update(update)\
#         .match(match)\
#         .execute()
#
#
# if __name__ == "__main__":
#     files = get_all_filenames_ru(18, 1)
#     for f in files:
#         print(f.id, f.name_ru)
