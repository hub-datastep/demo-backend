import re
from io import BytesIO
from typing import Any, Generator

import pdfplumber
from fastapi import HTTPException, status
from pdfplumber import PDF

from model.file.utd.utd_entity_params_parsing import (
    normalize_date,
    format_param,
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
    "Наименование товара (описание выполненных работ, оказанных услуг), "
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


def _clean_column_name(column_name: str) -> str:
    """
    Функция для очистки названий колонок от лишних пробелов и символов перевода строки.
    """
    return " ".join(column_name.replace("\n", " ").split())


def extract_noms_from_pages(
    pdf: PDF,
    pages_numbers_list: list[int],
    idn_file_guid: str,
) -> list[MaterialWithParams]:
    nomenclatures_with_params_list: list[MaterialWithParams] = []

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
                any(keyword in cell for keyword in _HEADERS_KEYWORDS)
                for cell in header_row
            )
            if is_header_row_contains_any_keyword:
                # Найден новый заголовок, сбрасываем текущие данные
                current_header = header_row
                header_indices = [
                    i
                    for i, cell in enumerate(header_row)
                    if any(keyword in cell for keyword in _HEADERS_KEYWORDS)
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

        # Извлечение данных из combined_table_rows с использованием header_indices
        for row in combined_table_rows:
            for index in header_indices:
                material_name = row[index]

                if len(row) > index and material_name:
                    material_name = material_name.strip().replace("\n", " ")

                    if len(material_name) > 2:
                        # Get params values by index from material index
                        quantity = row[index + 4]
                        price = row[index + 5]
                        cost = row[index + 6]
                        vat_rate = row[index + 8]
                        vat_amount = row[index + 9]

                        nomenclatures_with_params_list.append(
                            MaterialWithParams(
                                idn_material_name=material_name,
                                quantity=format_param(quantity, to_number=True),
                                price=format_param(price, to_number=True),
                                cost=format_param(cost, to_number=True),
                                vat_rate=format_param(vat_rate, to_number=True),
                                vat_amount=format_param(vat_amount, to_number=True),
                            )
                        )

    # If no nomenclatures was parsed
    if len(nomenclatures_with_params_list) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse nomenclatures from PDF file "
            f"with IDN file guid '{idn_file_guid}'",
        )

    return nomenclatures_with_params_list


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
                detail=f"PDF file with IDN file guid '{idn_file_guid}' is scan, "
                f"but text is required.",
            )


if __name__ == "__main__":
    pdf_file = (
        "/home/syrnnik/Downloads/unistroy/UPDs-17-09-2024/УПД Царево 1.1, 1.2.pdf"
    )

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
