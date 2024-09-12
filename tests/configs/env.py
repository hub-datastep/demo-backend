import os

from dotenv import load_dotenv

load_dotenv()

TESTS_API_URL = os.getenv('TESTS_API_URL')
TEST_AUTH_USERNAME = os.getenv('TEST_AUTH_USERNAME')
TEST_AUTH_PASSWORD = os.getenv('TEST_AUTH_PASSWORD')

# URL для авторизации и API
AUTH_URL = f"{TESTS_API_URL}/auth/sign_in"
