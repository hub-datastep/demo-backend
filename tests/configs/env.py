from dotenv import load_dotenv
from pydantic import BaseSettings

from infra.environment_type import EnvironmentType
from util.env_files import get_envfile_path
from util.path_to_file_or_dir import find_path_to_file_or_dir

_ENV_PATH = get_envfile_path(EnvironmentType.TEST)

load_dotenv(dotenv_path=_ENV_PATH)


class Env(BaseSettings):

    # API
    TESTS_API_URL: str = "http://localhost:8090/api/v1"
    TESTS_AUTH_USERNAME: str
    TESTS_AUTH_PASSWORD: str

    DATA_FOLDER_PATH: str = find_path_to_file_or_dir("data")

    # Google Sheets
    TESTS_SPREADSHEET_NAME: str
    TESTS_TABLE_NAME: str

    # Orders Classification Config
    TESTS_CONFIG_USER_ID: int | None

    # API Authorization
    def get_api_route_url(self, route: str) -> str:
        return f"{self.TESTS_API_URL}/{route}"

    # noinspection PyPep8Naming
    @property
    def GOOGLE_CREDENTIALS_PATH(self) -> str:
        return f"{self.DATA_FOLDER_PATH}/datastep-google-credentials.json"


env = Env()
