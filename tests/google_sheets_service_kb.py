import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pandas as pd
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

from infra.env import DATA_FOLDER_PATH

load_dotenv()

CREDENTIALS_PATH = f"{DATA_FOLDER_PATH}/datastep-excel-for-classifier-66a610dc9ff6.json"

TEST_CASES_TABLE_HEADERS = ['Тест-Кейс ID', 'Тип вопроса', 'Вопрос', 'Ожидаемый файл',
                            'Ожидаемый ответ', 'Комментарий']

TEST_KNOWLEDGE_BASE_SPREADSHEET_NAME = os.getenv('TEST_KNOWLEDGE_BASE_SPREADSHEET_NAME')
TEST_KNOWLEDGE_BASE_TEST_CASES_TABLE_NAME = os.getenv('TEST_KNOWLEDGE_BASE_TEST_CASES_TABLE_NAME')


def get_google_sheets_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Авторизация
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
    client = gspread.authorize(creds)

    return client


def get_sheet_headers(spreadsheet_name, sheet_name):
    client = get_google_sheets_client()
    sheet = client.open(spreadsheet_name).worksheet(sheet_name)
    headers = sheet.row_values(1)  # Получаем значения первой строки (заголовки)
    return headers


def read_sheet(spreadsheet_name, sheet_name, expected_headers):
    client = get_google_sheets_client()
    sheet = client.open(spreadsheet_name).worksheet(sheet_name)
    return sheet.get_all_records(expected_headers=expected_headers)


def write_to_sheet(spreadsheet_name, sheet_name, data):
    client = get_google_sheets_client()
    sheet = client.open(spreadsheet_name).worksheet(sheet_name)
    sheet.append_row(data)


def get_test_cases():
    return read_sheet(TEST_KNOWLEDGE_BASE_SPREADSHEET_NAME, TEST_KNOWLEDGE_BASE_TEST_CASES_TABLE_NAME,
                      TEST_CASES_TABLE_HEADERS)


def create_new_sheet_and_write_results(new_sheet_name, processed_results):
    client = get_google_sheets_client()
    spreadsheet = client.open(TEST_KNOWLEDGE_BASE_SPREADSHEET_NAME)
    new_sheet = spreadsheet.add_worksheet(title=new_sheet_name, rows=100, cols=20)

    headers = ['Тест-Кейс ID', 'Вопрос', 'Ожидаемый файл', 'Реальный файл', 'Ожидаемый ответ',
               'Реальный ответ', 'Корректно?', 'Тип вопроса', 'Комментарий']
    new_sheet.insert_row(headers, 1)

    for i, result in enumerate(processed_results, start=2):
        row = [
            result['Тест-Кейс ID'],
            result['Вопрос'],
            result['Ожидаемый файл'],
            result['Реальный файл'],
            result['Ожидаемый ответ'],
            result['Реальный ответ'],
            result['Корректно?'],
            result['Тип вопроса'],
            result['Комментарий']
        ]
        new_sheet.insert_row(row, i)
    print(f"Результаты тестов успешно сохранены: {new_sheet.url}")


def create_new_offline_sheet_and_write_results(new_sheet_name, processed_results):
    headers = ['Тест-Кейс ID', 'Вопрос', 'Ожидаемый файл', 'Реальный файл', 'Ожидаемый ответ',
               'Реальный ответ', 'Корректно?', 'Тип вопроса', 'Комментарий']

    # Преобразуем данные в DataFrame
    df = pd.DataFrame(processed_results, columns=headers)

    # Сохраняем DataFrame в Excel файл
    file_path = f"{new_sheet_name}.xlsx"
    df.to_excel(file_path, index=False)
    print(f"Результаты тестов успешно сохранены: {file_path}")
