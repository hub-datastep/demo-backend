from fastapi import HTTPException, status
from rq.command import send_stop_job_command
from rq.exceptions import InvalidJobOperation
from rq.registry import StartedJobRegistry

from infra.redis_queue import get_redis_connection, QueueName


def get_all_active_jobs():
    redis = get_redis_connection()
    queues_list = [value for key, value in vars(QueueName).items() if not key.startswith('__')]

    jobs_ids = []
    for queue in queues_list:
        registry = StartedJobRegistry(queue, connection=redis)
        running_job_ids = registry.get_job_ids()
        jobs_ids.extend(running_job_ids)

    return jobs_ids


def stop_job_by_id(job_id: str):
    redis = get_redis_connection()
    try:
        send_stop_job_command(redis, job_id)
    except InvalidJobOperation as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )
