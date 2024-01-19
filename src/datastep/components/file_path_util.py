import os
from pathlib import Path


def get_file_folder_path(storage_filename: str) -> Path:
    data_folder_path = Path(__file__).parent / "../../../data"
    # Split the original filename into name and extension
    file_folder_name, _ = os.path.splitext(storage_filename)
    return data_folder_path / file_folder_name
