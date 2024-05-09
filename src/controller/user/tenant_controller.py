from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model.auth_model import get_current_user
from repository import tenant_repository
from scheme.tenant_scheme import TenantRead, TenantCreate
from scheme.user_scheme import UserRead

router = APIRouter()


@router.post("", response_model=TenantRead)
@version(1)
def create_tenant(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    tenant: TenantCreate
):
    """
    """
    return tenant_repository.create_tenant(session, tenant)


# @router.get("/{tenant_id}/instruction", response_model=InstructionDto)
# @version(1)
# def get_instruction(
#     *,
#     current_user: UserRead = Depends(get_current_user),
#     tenant_id: int
# ):
#     return instruction_repository.get_instruction_by_tenant_id(tenant_id)

