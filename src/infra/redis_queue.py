from enum import Enum

from fastapi import HTTPException, status
from redis import Redis
from rq.exceptions import NoSuchJobError
from rq.job import Job
from rq.queue import Queue

from infra.env import env

# 1 day
MAX_JOB_TIMEOUT = 60 * 60 * 24


class QueueName:
    MAPPING = "mapping_nomenclatures"
    SYNCING = "sync_nomenclatures"
    RETRAINING = "retrain_classifier"
    CLASSIFICATION = "classification"
    DOCUMENTS = "documents"


# Enum for "clear queue endpoint"
QueuesEnum = Enum(
    "QueuesEnum",
    {
        attr: value for attr, value in QueueName.__dict__.items() if
        not attr.startswith('__') and not callable(getattr(QueueName, attr))
    }
)


def get_queues_list():
    queues_list: list[str] = [value for key, value in vars(QueueName).items() if
                              not key.startswith('__')]
    return queues_list


def get_redis_connection():
    redis = Redis(
        host=env.REDIS_HOST,
        port=env.REDIS_PORT,
        password=env.REDIS_PASSWORD,
    )
    return redis


def get_redis_queue(name: str):
    redis = get_redis_connection()
    queue = Queue(
        name=name,
        connection=redis,
    )
    return queue


def get_job(job_id: str):
    redis = get_redis_connection()
    try:
        job = Job.fetch(
            id=job_id,
            connection=redis,
        )
        return job
    except NoSuchJobError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )
