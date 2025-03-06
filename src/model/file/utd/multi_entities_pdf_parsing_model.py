import re
from io import BytesIO
from typing import Any, Generator

import pdfplumber
from fastapi import HTTPException, status
from pdfplumber import PDF

from model.file.utd.utd_entity_params_parsing import (
    normalize_date,
    format_param_value,
    get_organization_inn,
    get_supplier_inn,
    get_contract_params,
    get_correction_params,
    get_utd_number,
    get_utd_date_str,
)
from scheme.file.utd_card_message_scheme import (
    UTDEntityWithParamsAndNoms,
    MaterialWithParams,
    UTDEntityParams,
)

# Ключевые слова для поиска столбцов с наименованием товара
_HEADERS_KEYWORDS = [
    "Наименование товара",
    "Товары (работы, услуги)",
    "Наименование товара (описание выполненных работ, оказанных услуг),"
    "имущественного права",
]


def extract_params_from_page_text(
    page_text: str,
) -> UTDEntityParams:
    page_text = re.sub(r"\s+", " ", page_text)

    extracted_params = UTDEntityParams()

    # Get UTD number
    utd_number = get_utd_number(page_text)
    if utd_number is not None:
        extracted_params.idn_number = utd_number

    # Get UTD date
    utd_date_str = get_utd_date_str(page_text)
    if utd_date_str is not None:
        extracted_params.idn_date = normalize_date(date_str=utd_date_str)

    # Get organization INN
    organization_inn = get_organization_inn(page_text)
    if organization_inn is not None:
        extracted_params.organization_inn = organization_inn

    # Get supplier INN
    supplier_inn = get_supplier_inn(page_text)
    if supplier_inn is not None:
        extracted_params.supplier_inn = supplier_inn

    # Get correction number and date
    correction_number, correction_date = get_correction_params(page_text)
    if correction_number is not None:
        extracted_params.correction_idn_number = correction_number
    if correction_date is not None:
        extracted_params.correction_idn_date = normalize_date(date_str=correction_date)

    # Get contract name and date
    contract_number, contract_name, contract_date = get_contract_params(page_text)
    if contract_number is not None:
        extracted_params.contract_number = contract_number
    if contract_name is not None:
        extracted_params.contract_name = contract_name
    if contract_date is not None:
        extracted_params.contract_date = normalize_date(date_str=contract_date)

    return extracted_params


def _clean_cell_value(cell_value: str | None = None) -> str:
    """
    Функция для очистки содержания ячеек от лишних пробелов и символов переноса строки.
    """

    # Return empty str if no column name
    if not cell_value:
        return ""

    cleaned_value = re.sub(r"[\n\s]+", " ", cell_value)
    cleaned_value = cleaned_value.strip()
    return cleaned_value


def _get_material_column_index(header_row: list[str]) -> int | None:
    # Перебираем все ячейки (названия колонок) в строке
    for i, cell in enumerate(header_row):
        # Для каждого заголовка перебираем кейворды
        for keyword in _HEADERS_KEYWORDS:
            # Если в заголовке есть кейворд колонки с материалом,
            # то возвращаем его индекс
            if keyword in cell:
                return i


def extract_materials_from_pages(
    pdf: PDF,
    pages_numbers_list: list[int],
    idn_file_guid: str,
) -> list[MaterialWithParams]:
    # Init materials list of all now from all passed pages
    materials_with_params_list: list[MaterialWithParams] = []

    # Все строки таблицы с материалами
    combined_materials_tables_rows: list[tuple[list[str | None], int]] = []

    # Parse PDF pages by numbers
    for page_number in pages_numbers_list:
        pdf_page = pdf.pages[page_number]

        # Перебираем все таблицы на странице, чтобы найти таблицу с материалами
        tables_list = pdf_page.extract_tables()
        for table in tables_list:
            # Пропускаем пустые таблицы
            if not table:
                continue

            # Индекс колонки с названием материала
            material_column_index: int | None = None

            # Перебираем все строки возможной таблицы с материалами,
            # пока не дойдём до нужных заголовков
            for i, row in enumerate(table):
                # Предобработка ячейки строки
                cleaned_row = [_clean_cell_value(cell) if cell else "" for cell in row]

                # Проверяем содержит ли строка ключевые слова заголовков
                material_column_index = _get_material_column_index(
                    header_row=cleaned_row,
                )
                # Если в строке нашёлся заголовок названий материалов,
                # то сохраняем все последующие строки этой таблицы
                if material_column_index is not None:
                    rows_with_materials = [
                        (row, material_column_index) for row in table[i + 1 :]
                    ]
                    combined_materials_tables_rows.extend(rows_with_materials)
                    break
                # Если в файле таблица с материалами разделена
                # и следующей её части нет заголовков,
                # то проверяем текущую строку по строке заголовков
                # Check if any rows of material tables already added
                elif combined_materials_tables_rows:
                    # Check if current row length equal rows length in combined list
                    # aka check if current row belongs to same table
                    prev_material_row, material_column_index = (
                        combined_materials_tables_rows[-1]
                    )
                    if len(cleaned_row) == len(prev_material_row):
                        rows_with_materials = [
                            (row, material_column_index) for row in table[i:]
                        ]
                        combined_materials_tables_rows.extend(rows_with_materials)

    # Извлечение данных из combined_table_rows с использованием header_indexes
    for row, material_column_index in combined_materials_tables_rows:
        # Проверям, что колонка с материалом существует в строке
        if material_column_index >= len(row):
            continue

        material_name = _clean_cell_value(row[material_column_index])

        # Проверяем, что ячейка с названием материала не пустая
        if not material_name:
            continue

        # Проверяем, что это действительно название материала
        # Пока что проверить можем только за счёт длины строки
        if len(material_name) <= 2:
            continue

        # Get params values by index from material index
        quantity = row[material_column_index + 4]
        price = row[material_column_index + 5]
        cost = row[material_column_index + 6]
        vat_rate = row[material_column_index + 8]
        vat_amount = row[material_column_index + 9]

        # Combined all params to Material with Params
        parsed_material = MaterialWithParams(
            idn_material_name=material_name,
            quantity=format_param_value(
                param_value=quantity,
                to_number=True,
            ),
            price=format_param_value(
                param_value=price,
                to_number=True,
            ),
            cost=format_param_value(
                param_value=cost,
                to_number=True,
            ),
            vat_rate=format_param_value(
                param_value=vat_rate,
                to_number=True,
            ),
            vat_amount=format_param_value(
                param_value=vat_amount,
                to_number=True,
            ),
        )

        materials_with_params_list.append(parsed_material)

    # If no nomenclatures was parsed
    if len(materials_with_params_list) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Не удалось вытащить материалы из Вашего файла, "
                "свяжить с тех. поддержкой и покажите им эту ошибку:\n\n"
                "Details: Failed to parse nomenclatures from PDF file "
                f"with IDN file guid '{idn_file_guid}'"
            ),
        )

    return materials_with_params_list


def get_entities_with_params(
    pdf: PDF,
) -> list[UTDEntityWithParamsAndNoms]:
    utd_entities: list[UTDEntityWithParamsAndNoms] = []

    last_utd_number: str | None = None
    for page_number, page in enumerate(pdf.pages):
        page_text = page.extract_text()

        # Get UTD params of page
        utd_params = extract_params_from_page_text(
            page_text=page_text,
        )

        if utd_params.idn_number is not None:
            last_utd_number = utd_params.idn_number
            utd_entities.append(UTDEntityWithParamsAndNoms(**utd_params.dict()))

        # Add page to UTD entity pages list
        for i, entity in enumerate(utd_entities):
            if entity.idn_number == last_utd_number:
                # Update entity empty params with parsed params
                entity_dict = entity.dict()
                utd_params_dict = utd_params.dict()
                for key, value in entity_dict.items():
                    if value is None and key in utd_params_dict:
                        entity_dict[key] = utd_params_dict[key]

                # Recreate entity object
                entity = UTDEntityWithParamsAndNoms(**entity_dict)
                entity.pages_numbers_list.append(page_number)

                utd_entities[i] = entity

    return utd_entities


def extract_entities_with_params_and_noms(
    pdf_file: BytesIO | str,
    idn_file_guid: str,
) -> Generator[UTDEntityWithParamsAndNoms, Any, None]:
    with pdfplumber.open(pdf_file) as pdf:
        has_text = any(page.extract_text() for page in pdf.pages)

        if has_text:
            entities_list = get_entities_with_params(
                pdf=pdf,
            )

            for entity in entities_list:
                materials_list = extract_materials_from_pages(
                    pdf=pdf,
                    pages_numbers_list=entity.pages_numbers_list,
                    idn_file_guid=idn_file_guid,
                )
                entity.nomenclatures_list = materials_list

                yield entity

        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    # Russian Error text for users
                    "Вы загрузили скан(картинку) УПД, а нужен PDF с текстом.\n\n"
                    # English Error text with details for developers
                    f"Details: PDF file with IDN file guid '{idn_file_guid}' is scan, "
                    "but text is required."
                ),
            )


if __name__ == "__main__":
    pdf_file = "/home/syrnnik/Downloads/unistroy/Универсальный_передаточный_документ_УПД_№00БФ_000074_от_19_02 (что-то не так было).pdf"
    # pdf_file = "/home/syrnnik/Downloads/unistroy/LLMapper/UTDs for demo/УПД арматура №553516_101402 от 31.10.2023.pdf"

    # Test only entities with params parsing
    # with pdfplumber.open(pdf_file) as pdf:
    #     for entity in get_entities_with_params(pdf=pdf):
    #         entity = entity.dict()
    #         for key, val in entity.items():
    #             print(f"{key}: {val}")
    #         print()

    # for entity in extract_entities_with_params_and_noms(
    #     pdf_file=pdf_file,
    #     idn_file_guid="test",
    # ):
    #     pass

    # Test all params parsing
    for entity in extract_entities_with_params_and_noms(
        pdf_file=pdf_file,
        idn_file_guid="test",
    ):
        entity = entity.dict()
        for key, val in entity.items():
            if key == "nomenclatures_list":
                print(f"{key}:")
                for nom in val:
                    for key1, val1 in nom.items():
                        if key1 == "idn_material_name":
                            print(f"    {key1}: {val1}")
                        else:
                            print(f"        {key1}: {val1}")
            else:
                print(f"{key}: {val}, Type: {type(val)}")
        print()
