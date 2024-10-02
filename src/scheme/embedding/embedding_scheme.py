from rq.job import JobStatus
from sqlmodel import SQLModel


class CreateAndSaveEmbeddingsUpload(SQLModel):
    db_con_str: str
    table_name: str
    collection_name: str
    chunk_size: int | None = 500


class CreateAndSaveEmbeddingsResult(SQLModel):
    job_id: str
    status: JobStatus
    general_status: str
    ready_count: int | None
    total_count: int | None
