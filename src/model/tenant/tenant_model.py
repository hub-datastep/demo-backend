from fastapi import HTTPException, status
from sqlmodel import Session

from repository.tenant import tenant_repository
from scheme.tenant.tenant_scheme import Tenant


def get_tenant_by_id(session: Session, tenant_id: int) -> Tenant:
    tenant = tenant_repository.get_tenant_by_id(
        session=session,
        tenant_id=tenant_id,
    )

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with ID {tenant_id} is not found.",
        )

    return tenant
