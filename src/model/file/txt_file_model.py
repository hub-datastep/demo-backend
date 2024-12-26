import os
import re
from pathlib import Path

from fastapi import UploadFile

from infra.env import DATA_FOLDER_PATH
from util.files_paths import get_filename_with_postfix


def _clean_text(text: str) -> str:
    text = text.replace("\\n", "\n").replace("\\\\", "\\")
    return re.sub(r"[\s\n]+", " ", text).strip()


def _save_file(file_object: UploadFile) -> str:
    file_name = file_object.filename
    filename_with_postfix = get_filename_with_postfix(file_name)
    file_path = f"{DATA_FOLDER_PATH}/TXTs/{filename_with_postfix}"
    file_folder_path = Path(file_path).parent

    # Create dir if not exists
    os.makedirs(file_folder_path, exist_ok=True)

    with open(file_path, "wb") as new_file:
        file_data = file_object.file.read()
        new_file.write(file_data)

    return file_path


def extract_noms(file_object: UploadFile) -> list[str]:
    file_path = _save_file(file_object)

    # Read Saved File
    with open(file_path) as f:
        # rows_list = f.readlines()
        rows_list = f.read().strip().split("\n")

    parsed_noms = [_clean_text(row) for row in rows_list]

    # logger.info(parsed_noms)
    return parsed_noms
