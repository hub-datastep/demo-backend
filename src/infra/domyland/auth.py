import requests
from fastapi import HTTPException

from infra.domyland.constants import DOMYLAND_APP_NAME, DOMYLAND_API_BASE_URL
from infra.env import env


def get_domyland_headers(auth_token: str | None = None):
    if auth_token is None:
        return {
            "AppName": DOMYLAND_APP_NAME,
        }

    return {
        "AppName": DOMYLAND_APP_NAME,
        "Authorization": auth_token,
    }


def _get_auth_token(
    username: str,
    password: str,
    tenant_name: str,
) -> str:
    req_body = {
        "email": username,
        "password": password,
        "tenantName": tenant_name,
    }

    response = requests.post(
        url=f"{DOMYLAND_API_BASE_URL}/auth",
        json=req_body,
        headers=get_domyland_headers(),
    )

    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Domyland Auth: {response.text}",
        )

    auth_token = response.json()["token"]
    return auth_token


def get_ai_account_auth_token():
    """
    Account for AI and classification.
    """

    return _get_auth_token(
        username=env.DOMYLAND_AUTH_AI_ACCOUNT_EMAIL,
        password=env.DOMYLAND_AUTH_AI_ACCOUNT_PASSWORD,
        tenant_name=env.DOMYLAND_AUTH_AI_ACCOUNT_TENANT_NAME,
    )


def get_public_account_auth_token():
    """
    Kind of Public Account for communication with residents.
    """

    return _get_auth_token(
        username=env.DOMYLAND_AUTH_PUBLIC_ACCOUNT_EMAIL,
        password=env.DOMYLAND_AUTH_PUBLIC_ACCOUNT_PASSWORD,
        tenant_name=env.DOMYLAND_AUTH_PUBLIC_ACCOUNT_TENANT_NAME,
    )
