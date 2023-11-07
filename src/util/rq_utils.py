from redis import Redis
from rq import Queue
from rq.job import Job
from rq.registry import FailedJobRegistry

redis = Redis()
queue = Queue(connection=redis)
registry = FailedJobRegistry(queue=queue)

# Show all failed job IDs and the exceptions they caused during runtime
for job_id in registry.get_job_ids():
    job = Job.fetch("5b65d4a2-b659-49f6-ae7a-9fd6f45095a5", connection=redis)
    print(job.get_status())
