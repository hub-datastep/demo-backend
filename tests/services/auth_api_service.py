import requests

from configs.env import TESTS_AUTH_USERNAME, TESTS_AUTH_PASSWORD, AUTH_URL

# Данные для авторизации
AUTH_PAYLOAD = {
    "grant_type": "password",
    "username": TESTS_AUTH_USERNAME,
    "password": TESTS_AUTH_PASSWORD,
}


def authenticate():
    response = requests.post(AUTH_URL, data=AUTH_PAYLOAD)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Authentication failed with status {response.status_code}. Details: {response.text}")


if __name__ == "__main__":
    authenticate()
