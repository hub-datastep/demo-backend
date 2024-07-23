from fastapi import HTTPException, status
from sqlmodel import Session

from repository.role import role_repository
from scheme.role.role_scheme import Role


def get_role_by_id(session: Session, role_id: int) -> Role:
    role = role_repository.get_role_by_id(session, role_id)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found.",
        )

    return role


def delete_role_by_id(session: Session, role_id: int) -> None:
    role = get_role_by_id(session, role_id)
    return role_repository.delete_role_by_id(session, role)
