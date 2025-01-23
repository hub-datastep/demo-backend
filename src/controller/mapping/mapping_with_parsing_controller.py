from fastapi import APIRouter, Depends
from fastapi_versioning import version

from model.auth.auth_model import get_current_user
from model.mapping import mapping_with_parsing_model
from scheme.file.utd_card_message_scheme import (
    UTDCardInputMessage,
    UTDCardOutputMessage,
)
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.post("/utd_card", response_model=UTDCardOutputMessage)
@version(1)
def parse_and_map_utd_card(
    body: UTDCardInputMessage,
    current_user: UserRead = Depends(get_current_user),
):
    return mapping_with_parsing_model.parse_and_map_utd_card(body=body)
