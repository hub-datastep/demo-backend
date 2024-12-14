from fastapi import APIRouter
from fastapi_versioning import version

from model.mapping import mapping_with_parsing_model
from scheme.parsing.parsing_scheme import UTDCardInputMessage, UTDCardOutputMessage

router = APIRouter()


@router.post("/utd", response_model=UTDCardOutputMessage)
@version(1)
def parse_and_map_utd_card(body: UTDCardInputMessage):
    return mapping_with_parsing_model.parse_and_map_utd_card(body=body)
