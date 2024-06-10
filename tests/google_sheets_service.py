import gspread
from oauth2client.service_account import ServiceAccountCredentials

from infra.env import DATA_FOLDER_PATH

CREDENTIALS_PATH = f"{DATA_FOLDER_PATH}/datastep-excel-for-classifier-66a610dc9ff6.json"

TEST_CASES_TABLE_HEADERS = ['Тест-Кейс ID', 'Шаг алгоритма', 'Тип ошибки', 'Номенклатура поставщика',
                            'Ожидание номенклатура', 'Ожидание группа']
SPREADSHEET_NAME = '[Unistroy noms] classifier test cases'
TEST_CASES_TABLE_NAME = 'test cases'


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
    return read_sheet(SPREADSHEET_NAME, TEST_CASES_TABLE_NAME, TEST_CASES_TABLE_HEADERS)


def create_new_sheet_and_write_results(new_sheet_name, processed_results):
    client = get_google_sheets_client()
    spreadsheet = client.open(SPREADSHEET_NAME)
    new_sheet = spreadsheet.add_worksheet(title=new_sheet_name, rows="100", cols="20")

    headers = ['Тест-Кейс ID', 'Шаг алгоритма', 'Тип ошибки', 'Корректно?', 'Номенклатура', 'Ожидание группа',
               'Реальность группа', 'Ожидание номенклатура', 'Реальность номенклатура']
    new_sheet.insert_row(headers, 1)

    for i, result in enumerate(processed_results, start=2):
        row = [
            result['Тест-Кейс ID'],
            result['Шаг алгоритма'],
            result['Тип ошибки'],
            result['Корректно?'],
            result['Номенклатура'],
            result['Ожидание группа'],
            result['Реальность группа'],
            result['Ожидание номенклатура'],
            result['Реальность номенклатура']
        ]
        new_sheet.insert_row(row, i)
