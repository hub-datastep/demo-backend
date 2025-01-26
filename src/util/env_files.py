import os
from pathlib import Path

from dotenv import load_dotenv

from infra.environment_type import EnvironmentType
from util.path_to_file_or_dir import find_path_to_file_or_dir


def get_current_environment_type() -> EnvironmentType:
    load_dotenv()

    # По умолчанию DEV
    environment_type = EnvironmentType(os.getenv("ENVIRONMENT", EnvironmentType.DEV))
    return environment_type


def get_envfile_path(env_type: EnvironmentType | None = None) -> Path:
    # Собираем название .env файла по типу среды
    if not env_type:
        env_type = get_current_environment_type()
    envfile_name = f".env.{env_type.value}"

    envfile_name = envfile_name.lower()
    return find_path_to_file_or_dir(envfile_name)


if __name__ == "__main__":
    # try:
    #     env_path = get_envfile_path(EnvironmentType.TEST)
    #     logger.success(f"Файл найден: {env_path}")
    # except FileNotFoundError as e:
    #     logger.error(e)

    print(get_current_environment_type())
