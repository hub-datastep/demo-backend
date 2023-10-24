from fastapi import APIRouter, Depends
from fastapi_versioning import version
from redis import Redis
from rq.exceptions import NoSuchJobError
from rq.job import Job
from rq.command import send_stop_job_command

from dto.file_upload_task_dto import FileUploadTaskDto
from model import file_model
from repository import file_repository
from dto.user_dto import UserDto
from service.auth_service import AuthService

router = APIRouter(
    prefix="/task",
    tags=["task"],
)


@router.get("/file_upload/active", response_model=list[FileUploadTaskDto])
@version(1)
def get_active_file_upload_tasks(current_user: UserDto = Depends(AuthService.get_current_user)):
    redis = Redis()
    try:
        job = Job.fetch(current_user.id, connection=redis)
    except NoSuchJobError:
        return []

    if job.get_status(refresh=True) in ["finished", "failed", "stopped"]:
        return []

    return [FileUploadTaskDto(
        id=job.id,
        status=job.get_status(refresh=True),
        progress=job.get_meta(refresh=True).get("progress", None),
        full_work=job.get_meta(refresh=True).get("full_work", None)
    )]


@router.delete("/file_upload/{task_id}", response_model=FileUploadTaskDto)
@version(1)
def interrupt_task_by_id(task_id: str | int, current_user: UserDto = Depends(AuthService.get_current_user)):
    redis = Redis()
    send_stop_job_command(redis, current_user.id)
    job = Job.fetch(current_user.id, connection=redis)

    file = file_repository.get_file_by_id(job.get_meta(refresh=True)["file_id"])
    file_model.delete_file(file)

    return FileUploadTaskDto(
        id=job.id,
        status=job.get_status(refresh=True),
        progress=job.get_meta(refresh=True).get("progress", None),
        full_work=job.get_meta(refresh=True).get("full_work", None)
    )
