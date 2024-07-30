from functools import wraps

from fastapi import status, HTTPException

from scheme.user.user_scheme import UserRead


class TenantMode:
    DOCS = 1
    DB = 2
    CLASSIFIER = 3


def modes_required(required_modes_ids: list[int]):
    def decorator(endpoint):
        # @wraps is needed to prevent overriding endpoint func name, docs and other
        @wraps(endpoint)
        def wrapper(*args, **kwargs):
            current_user: UserRead = kwargs.get("current_user")
            tenant_modes = current_user.tenant.modes

            for mode in tenant_modes:
                if mode.id in required_modes_ids:
                    return endpoint(*args, **kwargs)

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )

        return wrapper

    return decorator
