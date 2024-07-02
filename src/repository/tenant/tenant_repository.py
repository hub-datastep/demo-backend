from typing import Type

from fastapi import HTTPException
from sqlmodel import Session

from scheme.mode.mode_scheme import Mode
from scheme.tenant.tenant_scheme import TenantCreate, Tenant


def get_tenant_by_id(session: Session, tenant_id: int) -> Type[Tenant]:
    tenant_db = session.get(Tenant, tenant_id)

    if tenant_db is None:
        raise HTTPException(
            status_code=404,
            detail=f"Tenant with ID {tenant_id} is not found.",
        )

    return tenant_db


def create_tenant(session: Session, tenant: TenantCreate) -> Tenant:
    modes_db = [session.get(Mode, mode_id) for mode_id in tenant.modes]

    tenant_db = Tenant.from_orm(tenant)
    tenant_db.modes = modes_db

    session.add(tenant_db)
    session.commit()
    return tenant_db
