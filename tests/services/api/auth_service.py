import requests
from loguru import logger

from configs.env import env
from scheme.auth.token_scheme import Token

# Данные для авторизации
_PAYLOAD = {
    "grant_type": "password",
    "username": env.TESTS_AUTH_USERNAME,
    "password": env.TESTS_AUTH_PASSWORD,
}


def get_auth_token():
    response = requests.post(
        url=env.get_api_route_url(route="auth/sign_in"),
        data=_PAYLOAD,
    )

    if not response.ok:
        raise Exception(
            f"Authentication failed. "
            f"Status code {response.status_code}. "
            f"Details: {response.text}."
        )

    token = Token(**response.json())
    return token.access_token


def get_auth_headers():
    token = get_auth_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    return headers


if __name__ == "__main__":
    token = get_auth_token()
    logger.success(f"API Access Token: {token}")
