import os
import re
from pathlib import Path

import pdfplumber
from fastapi import UploadFile
from loguru import logger

from infra.env import DATA_FOLDER_PATH
from util.files_paths import get_filename_with_postfix


NOMENCLATURE_COLUMN_NAME = "Наименование и техническая характеристика"
NOM_COL_NAME = "Номенклатура на вход"


def _clean_text(text: str) -> str:
    return re.sub(r"[\s\n]+", " ", text).strip()


def _save_file(file_object: UploadFile) -> str:
    file_name = file_object.filename
    filename_with_postfix = get_filename_with_postfix(file_name)
    file_path = f"{DATA_FOLDER_PATH}/specs/{filename_with_postfix}"
    file_folder_path = Path(file_path).parent

    # Create dir if not exists
    os.makedirs(file_folder_path, exist_ok=True)

    with open(file_path, "wb") as new_file:
        file_data = file_object.file.read()
        new_file.write(file_data)

    return file_path


def extract_noms(file_object: UploadFile) -> list[str]:
    file_path = _save_file(file_object)

    parsed_noms = []
    try:
        with pdfplumber.open(file_path) as pdf:
            # logger.debug(f"Parsing {file_name}")
            # logger.debug(f"Pages count: {len(pdf.pages)}")

            for page in pdf.pages:
                if not page:
                    continue

                tables = page.extract_tables()

                for table in tables:
                    if not table:
                        continue
                    # logger.info(f"Table: {table}")

                    headers_list = table[0]

                    # Fix headers
                    headers_list = [
                        _clean_text(header) if header else None
                        for header in headers_list
                    ]
                    # logger.info(headers_list)

                    named_headers_list = [header for header in headers_list if header]

                    columns_count = len(named_headers_list)
                    # Check cols count for enginerka
                    is_9_cols = columns_count == 9
                    # logger.debug(f"Cols count: {columns_count}")
                    # logger.debug(f"Headers list: {named_headers_list}")
                    # logger.debug(f"Is 9 cols: {is_9_cols}")

                    if not is_9_cols:
                        continue

                    name_col_idx = next(
                        (
                            i
                            for i, val in enumerate(headers_list)
                            if val and NOMENCLATURE_COLUMN_NAME.lower() in val.lower()
                        ),
                        None,
                    )
                    is_name_col_exists = name_col_idx is not None
                    # logger.debug(f"Name col index: {name_col_idx}")

                    if not is_name_col_exists:
                        continue

                    features_col_idx = None
                    if is_name_col_exists:
                        features_col_idx = name_col_idx + 1

                    is_nomenclatures_table = is_name_col_exists and is_9_cols
                    # logger.debug(f"Is noms table: {is_nomenclatures_table}")

                    if not is_nomenclatures_table:
                        continue

                    # Start from second row in table (first is headers)
                    for i in range(1, len(table)):
                        row = table[i]

                        nomenclature = (
                            _clean_text(row[name_col_idx])
                            if name_col_idx and row[name_col_idx]
                            else None
                        )
                        # logger.info(f"Nomenclature: {nomenclature}, {type(nomenclature)}")
                        is_nom_exists = nomenclature is not None

                        if not is_nom_exists:
                            continue

                        features = (
                            _clean_text(row[features_col_idx])
                            if features_col_idx is not None and row[features_col_idx]
                            else None
                        )
                        # logger.info(f"Features: {features}, {type(features)}")
                        is_features_exists = features is not None

                        is_GOST_features = (
                            "ГОСТ".lower() in features.lower()
                            if is_features_exists
                            else False
                        )

                        if (
                            is_nom_exists
                            and is_features_exists
                            and not is_GOST_features
                        ):
                            nomenclature = f"{nomenclature} {features}"

                        nomenclature = nomenclature.strip()

                        parsed_noms.append(nomenclature)

    except ValueError as e:
        logger.error(file_path)
        logger.error(e)

    return parsed_noms
