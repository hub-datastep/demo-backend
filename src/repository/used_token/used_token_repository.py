from sqlmodel import Session

from infra.database import engine
from scheme.used_token.used_token_scheme import UsedToken


def create_used_token(used_token: UsedToken) -> UsedToken:
    with Session(engine) as session:
        session.add(used_token)
        session.commit()
        session.refresh(used_token)
        return used_token
