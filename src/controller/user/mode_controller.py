from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model.auth_model import get_current_user
from repository import mode_repository
from scheme.mode_scheme import ModeRead, ModeCreate
from scheme.user_scheme import UserRead

router = APIRouter()


@router.post("", response_model=ModeRead)
@version(1)
def create_mode(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    mode: ModeCreate
):
    """
    """
    return mode_repository.create_mode(session, mode)

# @router.get("/{tenant_id}/instruction", response_model=InstructionDto)
# @version(1)
# def get_instruction(
#     *,
#     current_user: UserRead = Depends(get_current_user),
#     tenant_id: int
# ):
#     return instruction_repository.get_instruction_by_tenant_id(tenant_id)
