from fastapi import APIRouter
from fastapi_versioning import version

from model.file.utd_parsing.parsing_job import parsing_job
from scheme.parsing.parsing_scheme import UTDCardInputMessage, UTDCardOutputMessage

router = APIRouter()


@router.post("/utd", response_model=UTDCardOutputMessage)
@version(1)
def parse_and_map_utd_card(body: UTDCardInputMessage):
    return parsing_job(body=body)
