from fastapi import HTTPException, status
from sqlmodel import Session

from repository.tenant import tenant_repository
from repository.user import user_repository
from scheme.user.user_scheme import User, UserCreate
from util.hashing import pwd_context


def get_user_by_id(session: Session, user_id: int):
    user = user_repository.get_user_by_id(
        session=session,
        user_id=user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    return user


def get_full_user_by_id(user_id: int):
    user = user_repository.get_full_user_by_id(user_id=user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    return user


def create_user(session: Session, user: UserCreate) -> User:
    try:
        user_db = user_repository.get_user_by_username(session, user.username)
    except HTTPException as e:
        if e.status_code != 404:
            raise HTTPException(status_code=400, detail=f"User with username={user.username} is already existed.")

        tenant_db = tenant_repository.get_tenant_by_id(session, user.tenant_id)

        hashed_password = pwd_context.hash(user.password)
        user_db = User(username=user.username, password=hashed_password)
        user_db.tenants = [tenant_db]
        session.add(user_db)
        session.commit()

    return user_db
