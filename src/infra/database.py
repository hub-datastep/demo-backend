import os

from sqlmodel import create_engine, SQLModel, Session

db_url = os.getenv("DB_CONNECTION_STRING")

engine = create_engine(db_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
