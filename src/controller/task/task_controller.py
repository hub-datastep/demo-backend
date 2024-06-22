from fastapi import APIRouter, Depends
from fastapi_versioning import version

from model import task_model
from model.auth_model import get_current_user
from scheme.task_scheme import RQJob
from scheme.user_scheme import UserRead

router = APIRouter()


@router.get("/", response_model=list[RQJob])
@version(1)
def get_all_jobs(current_user: UserRead = Depends(get_current_user)) -> list[RQJob]:
    return task_model.get_all_jobs()


@router.delete("/stop_job/{job_id}")
@version(1)
def stop_job_by_id(job_id: str, current_user: UserRead = Depends(get_current_user)):
    return task_model.stop_job_by_id(job_id)
