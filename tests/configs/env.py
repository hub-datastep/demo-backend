import os

from dotenv import load_dotenv

load_dotenv()

TESTS_API_URL = os.getenv('TESTS_API_URL')
TESTS_AUTH_USERNAME = os.getenv('TESTS_AUTH_USERNAME')
TESTS_AUTH_PASSWORD = os.getenv('TESTS_AUTH_PASSWORD')

assert TESTS_API_URL, "TESTS_API_URL is not set in .env"
assert TESTS_AUTH_USERNAME, "TESTS_AUTH_USERNAME is not set in .env"
assert TESTS_AUTH_PASSWORD, "TESTS_AUTH_PASSWORD is not set in .env"

# URL для авторизации и API
AUTH_URL = f"{TESTS_API_URL}/auth/sign_in"
