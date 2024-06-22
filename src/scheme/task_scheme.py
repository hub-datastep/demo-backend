from rq.job import JobStatus
from sqlmodel import SQLModel


class RQJob(SQLModel):
    job_id: str
    status: JobStatus
    queue: str
