from sqlmodel import Session

from scheme.mode.mode_scheme import Mode
from scheme.tenant.tenant_scheme import TenantCreate, Tenant, TenantUpdate


def get_tenant_by_id(session: Session, tenant_id: int) -> Tenant | None:
    tenant = session.get(Tenant, tenant_id)
    return tenant


def create_tenant(session: Session, tenant: TenantCreate) -> Tenant:
    modes_db = [session.get(Mode, mode_id) for mode_id in tenant.modes]

    tenant_db = Tenant.from_orm(tenant)
    tenant_db.modes = modes_db

    session.add(tenant_db)
    session.commit()
    return tenant_db


def update_tenant_by_id(session: Session, tenant: TenantUpdate) -> Tenant:
    modes_db = [session.get(Mode, mode_id) for mode_id in tenant.modes]

    tenant_db = Tenant.from_orm(tenant)
    tenant_db.modes = modes_db

    session.merge(tenant_db)
    session.commit()
    return tenant_db
