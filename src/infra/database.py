from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from infra.env import env

engine = create_engine(
    env.DB_CONNECTION_STRING,
    # Show additional logs from DB
    # True = show, False = not show
    echo=False,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def create_session_by_db_con_str(db_con_str: str) -> Session:
    engine = create_engine(db_con_str)
    session = Session(engine)
    return session
