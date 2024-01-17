from typing import Type

from fastapi import HTTPException
from sqlmodel import Session, select

from scheme.user_scheme import UserCreate, User
from util.hashing import get_password_hash


def get_user_by_id(session: Session, user_id: int) -> Type[User]:
    user_db = session.get(User, user_id)

    if user_db is None:
        raise HTTPException(status_code=404, detail=f"User with chat_id={user_id} is not found.")

    return user_db


def get_user_by_username(session: Session, username: str) -> User:
    statement = select(User).where(User.username == username)
    result = session.exec(statement)
    user_db = result.first()

    if user_db is None:
        raise HTTPException(status_code=404, detail=f"User with username={username} is not found.")

    return user_db


def create_user(session: Session, user: UserCreate) -> User:
    user.password = get_password_hash(user.password)
    user_db = User.from_orm(user)
    session.add(user_db)
    session.commit()
    return user_db
