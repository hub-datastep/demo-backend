from sqlmodel import Session, select, extract

from infra.database import engine
from scheme.used_token.used_token_scheme import UsedToken


def get_tenant_used_tokens_by_month(session: Session, tenant_id: int, month: int) -> list[UsedToken]:
    st = select(UsedToken).where(
        UsedToken.tenant_id == tenant_id
    ).where(
        extract('month', UsedToken.used_at) == month
    )
    result = list(session.exec(st).all())
    return result


def create_used_token(used_token: UsedToken) -> UsedToken:
    with Session(engine) as session:
        session.add(used_token)
        session.commit()
        session.refresh(used_token)
        return used_token
