from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from repository import tenant_repository
from scheme.tenant_scheme import TenantRead, TenantCreate

router = APIRouter(
    prefix="/tenant",
    tags=["tenant"],
)


@router.post("", response_model=TenantRead)
@version(1)
def create_tenant(*, session: Session = Depends(get_session), tenant: TenantCreate):
    return tenant_repository.create_tenant(session, tenant)
