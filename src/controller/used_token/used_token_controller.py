from fastapi import APIRouter, Depends, Query
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from middleware.role_middleware import admins_only
from model.auth.auth_model import get_current_user
from model.used_token import used_token_model
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("/{tenant_id}", response_model=int)
@version(1)
@admins_only
def get_tenant_used_tokens_by_month(
    tenant_id: int,
    month: int | None = Query(
        None,
        description="Month number, e.g. 1 is Jan. **Default:** _current month_",
    ),
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
) -> int:
    """
    Получает количество потраченных токенов тенанта за последний месяц.
    """
    return used_token_model.get_tenant_used_tokens_by_month(session, tenant_id, month)
