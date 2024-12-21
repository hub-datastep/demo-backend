from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from infra.database import engine
from scheme.user.user_scheme import UserCreate, User, UserUpdate
from util.hashing import get_password_hash


def get_user_by_id(session: Session, user_id: int) -> User:
    user = session.get(User, user_id)
    return user


def get_full_user_by_id(user_id: int):
    with Session(engine) as session:
        st = select(User)
        st = st.where(User.id == user_id)
        st = st.options(
            joinedload(User.classifier_config),
        )

        user = session.exec(st).first()

        return user


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


def update_user(session: Session, user: UserUpdate) -> User:
    if user.password is not None:
        user.password = get_password_hash(user.password)

    user_db = User.from_orm(user)
    session.merge(user_db)
    session.commit()
    return user_db
