import requests

from configs.env import TEST_AUTH_USERNAME, TEST_AUTH_PASSWORD, AUTH_URL

# Данные для авторизации
AUTH_PAYLOAD = {
    "grant_type": "password",
    "username": TEST_AUTH_USERNAME,
    "password": TEST_AUTH_PASSWORD,
}


def authenticate():
    response = requests.post(AUTH_URL, data=AUTH_PAYLOAD)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception("Authentication failed")
