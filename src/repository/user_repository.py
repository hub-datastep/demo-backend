from typing import Type

from fastapi import HTTPException

from sqlmodel import Session

from scheme.user_scheme import UserCreate, User


def get_user_by_id(session: Session, user_id: int) -> Type[User]:
    user_db = session.get(User, user_id)

    if user_db is None:
        raise HTTPException(status_code=404, detail=f"User with chat_id={user_id} is not found.")

    return user_db


def create_user(session: Session, user: UserCreate) -> User:
    user_db = User.from_orm(user)
    session.add(user_db)
    session.commit()
    return user_db