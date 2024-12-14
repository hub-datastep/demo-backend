from io import BytesIO

import pdfplumber
from fastapi import HTTPException, status

# Ключевые слова для поиска столбцов с наименованием товара
_KEYWORDS = [
    "Наименование товара",
    "Товары (работы, услуги)",
    "Наименование товара (описание выполненных работ, оказанных услуг), имущественного права"
]


def _clean_column_name(column_name):
    """
    Функция для очистки названий колонок от лишних пробелов и символов перевода строки.
    """
    return ' '.join(column_name.replace('\n', ' ').split())


def extract_noms(
    pdf_file_content: BytesIO,
    idn_file_guid: str,
) -> list:
    # Множество для уникальных номенклатур
    unique_nomenclatures = set()

    with pdfplumber.open(pdf_file_content) as pdf:
        has_text = any(page.extract_text() for page in pdf.pages)

        if has_text:
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
                    header_row = [
                        _clean_column_name(cell)
                        if cell else ''
                        for cell in table[0]
                    ]

                    # Проверка, содержит ли строка заголовка ключевые слова
                    is_header_row_contains_any_keyword = any(
                        any(
                            keyword in cell
                            for keyword in _KEYWORDS
                        ) for cell in header_row
                    )
                    if is_header_row_contains_any_keyword:
                        # Найден новый заголовок, сбрасываем текущие данные
                        current_header = header_row
                        header_indices = [
                            i for i, cell in enumerate(header_row)
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
                            cleaned_value = row[index].strip().replace('\n', ' ')
                            unique_nomenclatures.add(cleaned_value)
                            f += 1

            if not f:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Failed to parse file with IDN guid '{idn_file_guid}'"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"File with IDN guid '{idn_file_guid}' is scan, but text is required."
            )

    return list(unique_nomenclatures)
