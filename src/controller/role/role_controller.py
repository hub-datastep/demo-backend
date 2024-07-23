from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model.auth.auth_model import get_current_user
from model.role import role_model
from repository.role import role_repository
from scheme.role.role_scheme import Role, RoleBase
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.post("", response_model=Role)
@version(1)
def create_role(
    role: RoleBase,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return role_repository.create_role(session, role)


@router.get("/{role_id}", response_model=Role)
@version(1)
def get_role_by_id(
    role_id: int,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return role_model.get_role_by_id(session, role_id)


@router.delete("/{role_id}", response_model=None)
@version(1)
def delete_role(
    role_id: int,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return role_model.delete_role_by_id(session, role_id)
