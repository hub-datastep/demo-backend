import os

from dotenv import load_dotenv

load_dotenv()

TESTS_API_URL = os.getenv('TESTS_API_URL')
TESTS_AUTH_USERNAME = os.getenv('TESTS_AUTH_USERNAME')
TESTS_AUTH_PASSWORD = os.getenv('TESTS_AUTH_PASSWORD')

assert TESTS_API_URL, "TESTS_API_URL is not set in .env"
assert TESTS_AUTH_USERNAME, "TESTS_AUTH_USERNAME is not set in .env"
assert TESTS_AUTH_PASSWORD, "TESTS_AUTH_PASSWORD is not set in .env"

# Mapping
TESTS_MAPPING_SPREADSHEET_NAME = os.getenv('TESTS_MAPPING_SPREADSHEET_NAME')
TESTS_MAPPING_TEST_CASES_TABLE_NAME = os.getenv('TESTS_MAPPING_TEST_CASES_TABLE_NAME')

# URL для авторизации и API
AUTH_URL = f"{TESTS_API_URL}/auth/sign_in"

# Order Classification Test
TESTS_ORDER_CLASSIFICATION_SPREADSHEET_NAME = os.getenv(
    "TESTS_ORDER_CLASSIFICATION_SPREADSHEET_NAME"
)
TESTS_ORDER_CLASSIFICATION_TABLE_NAME = os.getenv(
    "TESTS_ORDER_CLASSIFICATION_TABLE_NAME"
)
TESTS_ORDER_CLASSIFICATION_CONFIG_USER_ID = int(
    os.getenv("TESTS_ORDER_CLASSIFICATION_CONFIG_USER_ID")
)
