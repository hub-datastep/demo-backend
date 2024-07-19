from repository.used_token.used_token_repository import create_used_token
from scheme.used_token.used_token_scheme import UsedToken


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
