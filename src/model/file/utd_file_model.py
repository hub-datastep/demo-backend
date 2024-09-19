import os
import re
from pathlib import Path

import pdfplumber
from fastapi import UploadFile
from loguru import logger

from infra.env import DATA_FOLDER_PATH
from util.files_paths import get_filename_with_postfix

NOMENCLATURE_COLUMN_NAME = "наименование товара"


def _clean_text(text: str):
    return re.sub(r'[\s\n]+', ' ', text).strip()


def _save_utd_file(file_object: UploadFile):
    file_name = file_object.filename
    filename_with_postfix = get_filename_with_postfix(file_name)
    file_path = f"{DATA_FOLDER_PATH}/UTDs/{filename_with_postfix}"
    file_folder_path = Path(file_path).parent

    # Create dir UTDs if not exists
    os.makedirs(file_folder_path, exist_ok=True)

    with open(file_path, "wb") as new_file:
        file_data = file_object.file.read()
        new_file.write(file_data)

    return file_path


def extract_noms_from_utd(file_object: UploadFile):
    file_path = _save_utd_file(file_object)

    parsed_noms = []
    try:
        with pdfplumber.open(file_path) as pdf:
            # logger.debug(f"Parsing {pdf_path}")
            # logger.debug(f"Pages count: {len(pdf.pages)}")

            prev_name_col_idx = None
            for page in pdf.pages:
                table = page.extract_table()
                # logger.info(f"table: {table}")

                if table:
                    headers_list = table[0]

                    # Fix headers
                    headers_list = [
                        _clean_text(header) if header else None
                        for header in headers_list
                    ]
                    # logger.info(headers_list)

                    name_col_idx = next((
                        i for i, val in enumerate(headers_list)
                        if val and NOMENCLATURE_COLUMN_NAME in val.lower()
                    ), None)
                    # logger.debug(f"Name col index: {name_col_idx}")

                    if name_col_idx:
                        prev_name_col_idx = name_col_idx
                    else:
                        name_col_idx = prev_name_col_idx

                    columns_count = len(headers_list)
                    # logger.debug(f"Cols count: {columns_count}")

                    is_nomenclatures_table = name_col_idx is not None or columns_count == 16
                    # logger.debug(f"is_nomenclatures_table: {is_nomenclatures_table}")

                    if not is_nomenclatures_table:
                        continue

                    for i in range(0, len(table)):
                        row = table[i]
                        # logger.info(f"row: {row}")

                        # Check if table is cut or row contains headers
                        is_headers_row = False
                        for col_value in row:
                            if col_value:
                                if NOMENCLATURE_COLUMN_NAME in col_value.lower():
                                    # logger.info(f"col_value: {col_value}")
                                    is_headers_row = True
                            if is_headers_row:
                                break

                        if is_headers_row:
                            continue

                        nomenclature = _clean_text(
                            row[name_col_idx]
                        ) if name_col_idx and row[name_col_idx] else None
                        # logger.info(f"Nomenclature: {nomenclature}")

                        if nomenclature and len(nomenclature) > 5:
                            # logger.info(f"Nomenclature: {nomenclature}")
                            parsed_noms.append(nomenclature)

    except ValueError as e:
        logger.error(file_path)
        logger.error(e)

    # logger.info(parsed_noms)
    return parsed_noms
