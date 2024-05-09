from sqlmodel import create_engine, SQLModel, Session

from infra.env import DB_CONNECTION_STRING

engine = create_engine(DB_CONNECTION_STRING, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session


def create_session_by_db_con_str(db_con_str: str) -> Session:
    engine = create_engine(db_con_str)
    session = Session(engine)
    return session
