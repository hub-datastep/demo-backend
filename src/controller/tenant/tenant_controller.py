from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from middleware.role_middleware import admins_only
from model.auth.auth_model import get_current_user
from model.tenant import tenant_model
from repository.tenant import tenant_repository
from scheme.tenant.tenant_scheme import TenantCreate, TenantUpdate, TenantRead
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("/{tenant_id}", response_model=TenantRead)
@version(1)
@admins_only
def get_tenant_by_id(
    tenant_id: int,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    """
    return tenant_model.get_tenant_by_id(session, tenant_id)


@router.post("", response_model=TenantRead)
@version(1)
@admins_only
def create_tenant(
    tenant: TenantCreate,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    """
    return tenant_repository.create_tenant(session, tenant)


@router.put("", response_model=TenantRead)
@version(1)
@admins_only
def update_tenant_by_id(
    tenant: TenantUpdate,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    """
    return tenant_repository.update_tenant_by_id(session, tenant)
