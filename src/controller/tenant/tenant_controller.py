from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from middleware.role_middleware import admins_only
from model.auth.auth_model import get_current_user
from repository.tenant import tenant_repository
from scheme.tenant.tenant_scheme import TenantRead, TenantCreate
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.post("", response_model=TenantRead)
@version(1)
@admins_only
def create_tenant(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    tenant: TenantCreate
):
    """
    """
    return tenant_repository.create_tenant(session, tenant)
