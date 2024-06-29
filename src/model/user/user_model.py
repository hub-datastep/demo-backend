from fastapi import HTTPException
from sqlmodel import Session

from repository import tenant_repository, user_repository
from scheme.user.user_scheme import User, UserCreate
from util.hashing import pwd_context


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


