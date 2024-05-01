import os

from redis import Redis
from rq.job import Job
from rq.queue import Queue

from infra.env import REDIS_PASSWORD, REDIS_HOST

# 1 day
MAX_JOB_TIMEOUT = 60 * 60 * 24


class QueueName:
    MAPPING = "mapping_nomenclatures"
    SYNCING = "sync_nomenclatures"
    RETRAINING = "retrain_classifier"
    CLASSIFICATION = "classification"


def get_redis_connection():
    redis = Redis(host=REDIS_HOST, password=REDIS_PASSWORD)
    return redis


def get_redis_queue(name: str):
    redis = get_redis_connection()
    queue = Queue(name=name, connection=redis)
    return queue


def get_job(job_id: str):
    redis = get_redis_connection()
    job = Job.fetch(job_id, connection=redis)
    return job
