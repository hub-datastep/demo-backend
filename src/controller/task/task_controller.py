from fastapi import APIRouter, Depends
from fastapi_versioning import version

from infra.redis_queue import QueuesEnum
from middleware.role_middleware import admins_only
from model.auth.auth_model import get_current_user
from model.task import task_model
from scheme.task.task_scheme import RQJob
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("/", response_model=list[RQJob])
@version(1)
@admins_only
def get_all_jobs(
    current_user: UserRead = Depends(get_current_user),
) -> list[RQJob]:
    return task_model.get_all_jobs()


@router.post("/{queue_name}")
@version(1)
@admins_only
def cleanup_queue(
    queue_name: QueuesEnum,
    current_user: UserRead = Depends(get_current_user),
):
    return task_model.cleanup_queue(queue_name.value)


@router.delete("/stop_job/{job_id}")
@version(1)
@admins_only
def stop_job_by_id(
    job_id: str,
    current_user: UserRead = Depends(get_current_user),
):
    return task_model.stop_job_by_id(job_id)
