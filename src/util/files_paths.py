import os
from datetime import datetime
from pathlib import Path

from infra.env import DATA_FOLDER_PATH


def get_file_folder_path(filename: str) -> Path:
    # Split the filename into name and extension
    file_folder_name, _ = os.path.splitext(filename)
    return Path(f"{DATA_FOLDER_PATH}/{file_folder_name}")


def get_file_storage_path(filename: str) -> Path:
    # Split the filename into name and extension
    file_folder_name, _ = os.path.splitext(filename)
    return Path(f"{file_folder_name}/{filename}")


def _get_file_datetime_postfix() -> str:
    now_datetime_str = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    return now_datetime_str


def get_filename_with_postfix(filename: str):
    postfix = _get_file_datetime_postfix()
    file_name, ext = os.path.splitext(filename)

    # Формируем новый путь с постфиксом
    new_file_path = f"{file_name} {postfix}{ext}"

    return new_file_path
