import os
import sys
from datetime import datetime

from gspread import SpreadsheetNotFound, Worksheet, Spreadsheet
from loguru import logger
from pandas import DataFrame

from configs.env import env

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


def get_google_sheets_client():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        filename=env.CREDENTIALS_PATH,
        scopes=SCOPES,
    )
    client = gspread.authorize(creds)
    return client


def get_spreadsheet(spreadsheet_name: str) -> Spreadsheet:
    client = get_google_sheets_client()
    spreadsheet = client.open(spreadsheet_name)
    return spreadsheet


def get_sheet(
    spreadsheet_name: str,
    sheet_name: str,
) -> Worksheet:
    spreadsheet = get_spreadsheet(spreadsheet_name=spreadsheet_name)
    sheet = spreadsheet.worksheet(sheet_name)
    return sheet


def get_sheet_headers(
    spreadsheet_name: str,
    sheet_name: str,
) -> list[str]:
    sheet = get_sheet(
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
    )
    # Получаем значения первой строки (заголовки)
    headers = sheet.row_values(1)
    return headers


def read_sheet(
    spreadsheet_name: str,
    sheet_name: str,
    headers: list[str] | None = None,
) -> list[dict]:
    try:
        sheet = get_sheet(
            spreadsheet_name=spreadsheet_name,
            sheet_name=sheet_name,
        )
        all_records = sheet.get_all_records(expected_headers=headers)
        return all_records

    except SpreadsheetNotFound as e:
        raise ValueError(
            f"Spreadsheet '{spreadsheet_name}' not found. "
            f"Check if it's not XLSX or try publish it for service account."
        ) from e


def write_to_sheet(
    spreadsheet_name: str,
    sheet_name: str,
    data,
) -> None:
    sheet = get_sheet(
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
    )
    sheet.append_row(data)


def get_test_cases(
    spreadsheet_name: str,
    sheet_name: str,
    headers: list[str] | None = None,
) -> list[dict]:
    return read_sheet(
        spreadsheet_name=spreadsheet_name,
        sheet_name=sheet_name,
        headers=headers,
    )


def create_new_sheet_and_write_results(
    spreadsheet_name: str,
    new_sheet_name: str,
    processed_results: list[dict],
):
    spreadsheet = get_spreadsheet(spreadsheet_name=spreadsheet_name)

    df = DataFrame(processed_results)
    headers = df.columns

    new_sheet = spreadsheet.add_worksheet(
        title=new_sheet_name,
        rows=len(processed_results),
        cols=len(headers),
    )
    new_sheet.insert_row(headers)

    for i, result in enumerate(processed_results, start=2):
        new_sheet.insert_row(result, i)

    logger.success(f"Результаты тестов успешно сохранены: {new_sheet.url}")


def save_results_locally(
    new_sheet_name: str,
    processed_results: list[dict],
):
    # Преобразуем данные в DataFrame
    # df = pd.DataFrame(processed_results, columns=TESTS_RESULT_TABLE_HEADERS)
    df = DataFrame(processed_results)

    # Сохраняем DataFrame в Excel файл
    now_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    file_path = f"{new_sheet_name} {now_time}.xlsx"
    df.to_excel(file_path, index=False)

    logger.info(f"Результаты тестов успешно сохранены: {file_path}")
