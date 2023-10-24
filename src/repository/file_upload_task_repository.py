from dto.file_upload_task_dto import FileUploadTaskDto
from infra.supabase import supabase
from postgrest.base_request_builder import APIResponse
from dotenv import load_dotenv

load_dotenv()


def create_task(file_id: int, full_work) -> FileUploadTaskDto:
    body = {"file_id": file_id, "progress": 0, "full_work": full_work}
    response: APIResponse = supabase.table("file_upload_task").insert(body).execute()
    return FileUploadTaskDto(**response.data[0])


def get_task_by_id(task_id: int) -> FileUploadTaskDto:
    response: APIResponse = supabase.table("file_upload_task").select("*").eq("id", task_id).execute()
    return FileUploadTaskDto(**response.data[0])


def get_active_tasks(user_id: str) -> list[FileUploadTaskDto]:
    response: APIResponse = supabase\
        .table("file_upload_task")\
        .select("*, file!file_upload_task_file_id_fkey(chat(*, user_id))")\
        .eq("file.chat.user_id", user_id)\
        .eq("status", "active")\
        .execute()
    return [FileUploadTaskDto(**task) for task in response.data]


def increase_progress(task_id: int, amount: int) -> FileUploadTaskDto:
    response: APIResponse = supabase\
        .table("file_upload_task")\
        .update({"progress": amount})\
        .eq("id", task_id)\
        .execute()
    return FileUploadTaskDto(**response.data[0])


def update(task_id: int, update: dict) -> FileUploadTaskDto:
    response: APIResponse = supabase \
        .table("file_upload_task") \
        .update(update) \
        .eq("id", task_id) \
        .execute()
    return FileUploadTaskDto(**response.data[0])


if __name__ == "__main__":
    print(get_active_tasks("bbc76978-6f4a-4f16-b12e-ef7fd414df97"))
