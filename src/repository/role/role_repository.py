from sqlmodel import Session

from scheme.role.role_scheme import Role, RoleBase


def get_role_by_id(session: Session, role_id: int) -> Role | None:
    role = session.get(Role, role_id)
    return role


def create_role(session: Session, role: RoleBase) -> Role:
    role_db = Role.from_orm(role)
    session.add(role_db)
    session.commit()
    session.refresh(role_db)
    return role_db


def delete_role_by_id(session: Session, role: Role) -> None:
    session.delete(role)
    session.commit()
