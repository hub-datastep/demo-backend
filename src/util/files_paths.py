import os
from pathlib import Path

from infra.env import DATA_FOLDER_PATH


def get_file_folder_path(filename: str) -> Path:
    # Split the original filename into name and extension
    file_folder_name, _ = os.path.splitext(filename)
    return Path(f"{DATA_FOLDER_PATH}/{file_folder_name}")


def get_file_storage_path(filename: str) -> Path:
    # Split the original filename into name and extension
    file_folder_name, _ = os.path.splitext(filename)
    return Path(f"{file_folder_name}/{filename}")
