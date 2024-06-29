from fastapi import HTTPException, status
from rq.command import send_stop_job_command
from rq.exceptions import InvalidJobOperation
from rq.job import JobStatus
from rq.registry import FinishedJobRegistry, StartedJobRegistry, ScheduledJobRegistry, FailedJobRegistry, \
    clean_registries

from infra.redis_queue import get_redis_connection, get_queues_list, get_redis_queue
from scheme.task.task_scheme import RQJob

REGISTRIES = [
    (FinishedJobRegistry, JobStatus.FINISHED),
    (StartedJobRegistry, JobStatus.STARTED),
    (ScheduledJobRegistry, JobStatus.SCHEDULED),
    (FailedJobRegistry, JobStatus.FAILED),
]


def get_all_jobs() -> list[RQJob]:
    redis = get_redis_connection()
    queues_list = get_queues_list()

    jobs_list = []
    for queue in queues_list:
        for Registry, registry_status in REGISTRIES:
            registry = Registry(queue, connection=redis)
            jobs_ids: list[str] = registry.get_job_ids()

            for job_id in jobs_ids:
                rq_job = RQJob(
                    job_id=job_id,
                    status=registry_status,
                    queue=queue,
                )
                jobs_list.append(rq_job)

    return jobs_list


def cleanup_queue(queue_name: str):
    queue = get_redis_queue(queue_name)
    queue.empty()
    clean_registries(queue)


def stop_job_by_id(job_id: str):
    redis = get_redis_connection()
    try:
        send_stop_job_command(redis, job_id)
    except InvalidJobOperation as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )
