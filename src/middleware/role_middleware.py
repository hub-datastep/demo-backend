from functools import wraps

from fastapi import status, HTTPException

from scheme.user.user_scheme import UserRead


def admins_only(endpoint):
    # @wraps is needed to prevent overriding endpoint func name, docs and other
    @wraps(endpoint)
    def wrapper(*args, **kwargs):
        current_user: UserRead = kwargs.get("current_user")
        user_role = current_user.role
        is_user_admin = user_role.name.lower() == "admin"

        if not is_user_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )

        return endpoint(*args, **kwargs)

    return wrapper
