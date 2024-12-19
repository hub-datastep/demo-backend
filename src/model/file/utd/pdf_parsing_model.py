import re
from datetime import datetime, date
from io import BytesIO

import pdfplumber
from fastapi import HTTPException, status
from pdfplumber import PDF

from scheme.file.utd_card_message_scheme import UTDParamsWithNomenclatures

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
    "invoice_number": r"Счет-фактура\s*№\s*([\w-]+)",
    "seller_inn": r"ИНН[\/КПП продавца]*[:\s]*([0-9]{10})",
}

_INVOICE_DATE_PATTERN = (
    r"Счет-фактура[^\n]*?от\s*(\d{1,2}[\.\s][а-яА-Я]+[\.\s]\d{4}|\d{2}\.\d{2}\.\d{4})"
)


def _clean_column_name(column_name: str) -> str:
    """
    Функция для очистки названий колонок от лишних пробелов и символов перевода строки.
    """
    return " ".join(column_name.replace("\n", " ").split())


def _normalize_date(date_str: str) -> date | None:
    """Функция для нормализации дат в формате DD.MM.YYYY."""

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


def extract_noms(
    pdf: PDF,
    idn_file_guid: str,
) -> list[str]:
    # Множество для уникальных номенклатур
    unique_nomenclatures = set()

    # Все строки данных
    combined_table_rows = []
    # Текущая строка заголовка
    current_header = None
    # Индексы нужных столбцов
    header_indices = []

    # TODO: rename 'f' param to more understandable name
    f = 0
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if not table:
                # Пропускаем пустые таблицы
                continue

            # Очистка строки заголовка
            header_row = [_clean_column_name(cell) if cell else "" for cell in table[0]]

            # Проверка, содержит ли строка заголовка ключевые слова
            is_header_row_contains_any_keyword = any(
                any(keyword in cell for keyword in _KEYWORDS) for cell in header_row
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
                    unique_nomenclatures.add(cleaned_value)
                    f += 1

    if not f:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse noms from file with IDN guid '{idn_file_guid}'",
        )

    noms_list = list(unique_nomenclatures)

    return noms_list


def extract_full_text(
    pdf: PDF,
) -> str:
    full_text = ""

    for page in pdf.pages:
        if page.rotation in [90, 270]:
            extracted_text = page.extract_text(orientation="vertical")
        else:
            extracted_text = page.extract_text()
        full_text += extracted_text if extracted_text else ""

    return full_text


def extract_params(
    pdf: PDF,
) -> UTDParamsWithNomenclatures:
    full_text = extract_full_text(pdf=pdf)
    full_text = re.sub(r"\s+", " ", full_text)

    extracted_params = UTDParamsWithNomenclatures()

    for param_name, pattern in _PARAMS_PATTERNS.items():
        match = re.search(pattern, full_text, re.IGNORECASE)
        param_value = match.group(1) if match else None
        setattr(extracted_params, param_name, param_value)

    invoice_date_str_match = re.search(_INVOICE_DATE_PATTERN, full_text, re.IGNORECASE)
    invoice_date_str = (
        invoice_date_str_match.group(1) if invoice_date_str_match else None
    )
    if invoice_date_str is not None:
        extracted_params.invoice_date = _normalize_date(
            date_str=invoice_date_str,
        )

    return extracted_params


def extract_params_and_noms(
    pdf_file_content: BytesIO,
    idn_file_guid: str,
) -> UTDParamsWithNomenclatures:
    with pdfplumber.open(pdf_file_content) as pdf:
        has_text = any(page.extract_text() for page in pdf.pages)

        if has_text:
            noms_list = extract_noms(
                pdf=pdf,
                idn_file_guid=idn_file_guid,
            )

            extracted_params = extract_params(
                pdf=pdf,
            )
            extracted_params.nomenclatures_list = noms_list

        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"File with IDN guid '{idn_file_guid}' is scan, but text is required.",
            )

    return extracted_params
