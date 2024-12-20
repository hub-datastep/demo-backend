import re
from datetime import datetime, date
from io import BytesIO

import pdfplumber
from fastapi import HTTPException, status
from pdfplumber import PDF

from scheme.file.utd_card_message_scheme import UTDEntityWithParamsAndNoms

# Ключевые слова для поиска столбцов с наименованием товара
_KEYWORDS = [
    "Наименование товара",
    "Товары (работы, услуги)",
    "Наименование товара (описание выполненных работ, оказанных услуг), имущественного права",
]

_MONTHS_NAME_AND_NUMBER_STR = {
    "января": "01",
    "февраля": "02",
    "марта": "03",
    "апреля": "04",
    "мая": "05",
    "июня": "06",
    "июля": "07",
    "августа": "08",
    "сентября": "09",
    "октября": "10",
    "ноября": "11",
    "декабря": "12",
}

_PARAMS_PATTERNS = {
    "supplier_inn": r"ИНН[\/КПП продавца]*[:\s]*([0-9]{10})",
}

_UTD_NUMBER_PATTERN = r"Счет-фактура\s*№\s*([\w-]+)"

_UTD_DATE_PATTERN = (
    r"Счет-фактура[^\n]*?от\s*(\d{1,2}[\.\s][а-яА-Я]+[\.\s]\d{4}|\d{2}\.\d{2}\.\d{4})"
)


def _normalize_date(date_str: str) -> date | None:
    """Функция для нормализации дат в формате DD.MM.YYYY и тип datetime.date"""

    date_match = re.search(r"(\d{1,2})\s+([а-яА-Я]+)\s+(\d{4})", date_str)
    if date_match:
        day = date_match.group(1)
        month_name = date_match.group(2)
        year = date_match.group(3)

        month_num_str = _MONTHS_NAME_AND_NUMBER_STR.get(month_name.lower())
        if month_num_str:
            normalized_date = datetime.strptime(
                f"{day}.{month_num_str}.{year}", "%d.%m.%Y"
            ).date()
        else:
            # Handle case where month name is not found
            normalized_date = None
    else:
        # Handle case where no valid date is found
        normalized_date = None

    return normalized_date


def extract_params_from_page_text(
    page_text: str,
) -> UTDEntityWithParamsAndNoms:
    page_text = re.sub(r"\s+", " ", page_text)

    extracted_params = UTDEntityWithParamsAndNoms()

    # Get other IDN params
    for param_name, pattern in _PARAMS_PATTERNS.items():
        match = re.search(pattern, page_text, re.IGNORECASE)
        param_value = match.group(1) if match else None
        setattr(extracted_params, param_name, param_value)

    # Get IDN date
    utd_date_str_match = re.search(_UTD_DATE_PATTERN, page_text, re.IGNORECASE)
    utd_date_str = utd_date_str_match.group(1) if utd_date_str_match else None
    if utd_date_str is not None:
        extracted_params.idn_date = _normalize_date(
            date_str=utd_date_str,
        )

    return extracted_params


def _clean_column_name(column_name: str) -> str:
    """
    Функция для очистки названий колонок от лишних пробелов и символов перевода строки.
    """
    return " ".join(column_name.replace("\n", " ").split())


def extract_noms_from_pages(
    pdf: PDF,
    pages_numbers_list: list[int],
    idn_file_guid: str,
) -> list[str]:
    nomenclatures_list = []

    # Текущая строка заголовка
    current_header = None
    # Индексы нужных столбцов
    header_indices = []

    for page_number in pages_numbers_list:
        pdf_page = pdf.pages[page_number]

        # Все строки данных
        combined_table_rows = []

        tables = pdf_page.extract_tables()
        for table in tables:
            if not table:
                # Пропускаем пустые таблицы
                continue

            # Очистка строки заголовка
            header_row = [_clean_column_name(cell) if cell else "" for cell in table[0]]

            # Проверка, содержит ли строка заголовка ключевые слова
            is_header_row_contains_any_keyword = any(
                any(keyword in cell for keyword in _KEYWORDS)
                for cell in header_row
            )
            if is_header_row_contains_any_keyword:
                # Найден новый заголовок, сбрасываем текущие данные
                current_header = header_row
                header_indices = [
                    i
                    for i, cell in enumerate(header_row)
                    if any(keyword in cell for keyword in _KEYWORDS)
                ]
                combined_table_rows.extend(table[1:])
            elif current_header:
                # Проверяем, соответствует ли структура таблицы текущему заголовку
                if len(table[0]) == len(current_header):
                    combined_table_rows.extend(table)
                else:
                    # Структура не соответствует, возможно, новая таблица
                    current_header = None
                    header_indices = []
            else:
                # Нет заголовка и нет текущего заголовка, пропускаем таблицу
                pass

        # Извлечение данных из combined_table_rows с использованием header_indices
        for row in combined_table_rows:
            for index in header_indices:
                if len(row) > index and row[index]:
                    cleaned_value = row[index].strip().replace("\n", " ")
                    nomenclatures_list.append(cleaned_value)

    # If no nomenclatures was parsed
    if len(nomenclatures_list) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse nomenclatures from PDF file with IDN file guid '{idn_file_guid}'",
        )

    return nomenclatures_list


def get_entities_with_params(
    pdf: PDF,
) -> list[UTDEntityWithParamsAndNoms]:
    utd_entities: list[UTDEntityWithParamsAndNoms] = []

    last_utd_number: str | None = None
    for page_number, page in enumerate(pdf.pages):
        page_text = page.extract_text()

        # Search UTD number on page
        utd_entity_match = re.search(_UTD_NUMBER_PATTERN, page_text)
        # If found, set new UTD number as last
        if utd_entity_match:
            last_utd_number = utd_entity_match.group(1)
            # Get params of new UTD entity
            utd_params = extract_params_from_page_text(
                page_text=page_text,
            )
            # Update UTD number and add it to entities list
            utd_params.idn_number = last_utd_number
            utd_entities.append(utd_params)

        # Add page to UTD entity pages list
        for entity in utd_entities:
            if entity.idn_number == last_utd_number:
                entity.pages_numbers_list.append(page_number)

    return utd_entities


def extract_entities_with_params_and_noms(
    pdf_file: BytesIO | str,
    idn_file_guid: str,
):
    with pdfplumber.open(pdf_file) as pdf:
        has_text = any(page.extract_text() for page in pdf.pages)

        if has_text:
            entities_list = get_entities_with_params(
                pdf=pdf,
            )

            for entity in entities_list:
                nomenclatures_list = extract_noms_from_pages(
                    pdf=pdf,
                    pages_numbers_list=entity.pages_numbers_list,
                    idn_file_guid=idn_file_guid,
                )
                entity.nomenclatures_list = nomenclatures_list

                yield entity

        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"PDF file with IDN file guid '{idn_file_guid}' is scan, but text is required.",
            )
