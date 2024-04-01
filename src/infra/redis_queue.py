import os

from redis import Redis
from rq.job import Job
from rq.queue import Queue

# 1 day
MAX_JOB_TIMEOUT = 60 * 60 * 24


def get_redis_queue(name: str):
    redis = Redis(host=os.getenv("REDIS_HOST"), password=os.getenv("REDIS_PASSWORD"))
    queue = Queue(name=name, connection=redis)
    return queue


def get_job(job_id: str):
    redis = Redis(host=os.getenv("REDIS_HOST"), password=os.getenv("REDIS_PASSWORD"))
    job = Job.fetch(job_id, connection=redis)
    return job
