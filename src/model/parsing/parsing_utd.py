import pdfplumber
from io import BytesIO

def clean_column_name(column_name):
    """Функция для очистки названий колонок от лишних пробелов и символов перевода строки."""
    return ' '.join(column_name.replace('\n', ' ').split())

# Ключевые слова для поиска столбцов с наименованием товара
nomenclature_keywords = [
        "Наименование товара",
        "Товары (работы, услуги)",
        "Наименование товара (описание выполненных работ, оказанных услуг), имущественного права"
    ]


def parsing_utd_file(file:BytesIO, uuid:str) -> list:
    unique_nomenclature = set()  # Множество для уникальных номенклатур

    try:
        with pdfplumber.open(file) as pdf:
            has_text = any(page.extract_text() for page in pdf.pages)
            
            if has_text:
                combined_table_rows = []  # Все строки данных
                current_header = None  # Текущая строка заголовка
                header_indices = []  # Индексы нужных столбцов
                f = 0
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if not table:
                            continue  # Пропускаем пустые таблицы

                        # Очистка строки заголовка
                        header_row = [clean_column_name(cell) if cell else '' for cell in table[0]]

                        # Проверка, содержит ли строка заголовка ключевые слова
                        if any(any(keyword in cell for keyword in nomenclature_keywords) for cell in header_row):
                            # Найден новый заголовок, сбрасываем текущие данные
                            current_header = header_row
                            header_indices = [
                                i for i, cell in enumerate(header_row)
                                if any(keyword in cell for keyword in nomenclature_keywords)
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
                                unique_nomenclature.add(cleaned_value)
                                f+=1


                if not f:
                    return f'Мы не можем читать файл ({uuid}) данного содержания'
            else:
                return f"Файл ({uuid}) - скан"
    
    except Exception as e:
        return f"Ошибка при обработке файла ({uuid}): {e}"
    
    return list(unique_nomenclature) 
