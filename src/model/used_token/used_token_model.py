from fastapi import HTTPException, status
from sqlmodel import Session

from repository.used_token import used_token_repository
from repository.used_token.used_token_repository import create_used_token
from scheme.used_token.used_token_scheme import UsedToken
from util.dates import get_current_month


def count_used_tokens(nomenclatures: list) -> int:
    tokens_count = len(nomenclatures)
    return tokens_count


def charge_used_tokens(tokens_count: int, tenant_id: int, user_id: int):
    used_tokens = UsedToken(
        tokens_count=tokens_count,
        tenant_id=tenant_id,
        user_id=user_id,
    )
    create_used_token(used_tokens)


def get_tenant_used_tokens_by_month(
    session: Session,
    tenant_id: int,
    month: int | None,
) -> int:
    if month is None:
        month = get_current_month()

    print(month)

    if month < 1 or month > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Month must be 1-12.",
        )

    tenant_used_tokens = used_token_repository.get_tenant_used_tokens_by_month(
        session=session,
        tenant_id=tenant_id,
        month=month,
    )
    tokens_count = sum(used_token.tokens_count for used_token in tenant_used_tokens)
    return tokens_count
