from asyncio import sleep

from fastapi import APIRouter, WebSocket
from fastapi_versioning import version
from redis import Redis
from rq.job import Job

from dto.file_upload_task_dto import FileUploadTaskDto

router = APIRouter()


@router.websocket("/{job_id}")
@version(1)
async def websocket_endpoint(
    websocket: WebSocket,
    job_id: str
):
    await websocket.accept()
    redis = Redis()
    while True:
        job = Job.fetch(job_id, connection=redis)
        await websocket.send_text(
            FileUploadTaskDto(
                id=job.id,
                status=job.get_status(refresh=True),
                progress=job.get_meta(refresh=True).get("progress", None),
                full_work=job.get_meta(refresh=True).get("full_work", None)
            ).model_dump_json()
        )
        if job.get_status() in ["finished", "failed", "stopped"]:
            job.delete()
            await websocket.close()
            break
        await sleep(1)
