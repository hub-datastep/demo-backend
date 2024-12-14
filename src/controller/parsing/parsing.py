from fastapi import APIRouter
from fastapi_versioning import version
from scheme.parsing.parsing_scheme import UploadCardRequest
from model.parsing.parsing_job import parsing_job

router = APIRouter()

@router.post("")  # , response_model=UploadCardRequest) # response_model - ответ со строгой типизацией
@version(1)
def create_upload_card(request: UploadCardRequest):
    return parsing_job(request=request)
