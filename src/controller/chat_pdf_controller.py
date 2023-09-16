from fastapi import APIRouter, Depends, UploadFile
from fastapi_versioning import version
from starlette.responses import StreamingResponse

from dto.query_dto import QueryDto
from dto.user_dto import UserDto
from model import chat_pdf_model
from service.auth_service import AuthService

router = APIRouter(
    prefix="/chat_pdf",
    tags=["chat_pdf"],
)


@router.post("/prediction")
@version(1)
async def get_prediction(query: str, chat_id: int = None, file: UploadFile = None, current_user: UserDto = Depends(AuthService.get_current_user)):
    body = QueryDto(
        query=query,
        chat_id=chat_id,
        file=file
    )
    return StreamingResponse(chat_pdf_model.get_prediction(body), media_type="text/event-stream")
