from fastapi import APIRouter, WebSocket
from fastapi_versioning import version
from asyncio import sleep

from repository import file_upload_task_repository

router = APIRouter(
    prefix="/task/ws",
    tags=["task"],
)


@router.websocket("/{task_id}")
@version(1)
async def websocket_endpoint(
    websocket: WebSocket,
    task_id: int
):
    await websocket.accept()
    while True:
        task = file_upload_task_repository.get_task_by_id(task_id)
        await websocket.send_text(task.model_dump_json())
        if task.status != "active":
            await websocket.close()
            break
        await sleep(2)
