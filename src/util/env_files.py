from loguru import logger

from infra.environment_type import EnvironmentType
from util.files_paths import find_path_to_file_or_dir


def get_envfile_path(env_type: EnvironmentType):
    # Собираем название .env файла по типу среды
    envfile_name = f".env.{env_type.value}".lower()

    return find_path_to_file_or_dir(envfile_name)


if __name__ == "__main__":
    try:
        env_path = get_envfile_path(EnvironmentType.TEST)
        logger.success(f"Файл найден: {env_path}")
    except FileNotFoundError as e:
        logger.error(e)
