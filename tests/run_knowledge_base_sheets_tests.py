import logging
from datetime import datetime

from services.api_service_kb import authenticate, start_knowledge_base_prediction
from services.google_sheets_service_kb import get_test_cases, create_new_sheet_and_write_results
from utils.result_knowledge_base import process_results

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_tests():
    try:
        logging.info("Получение тест кейсов.")
        test_cases = get_test_cases()

        logging.info("Авторизация в API.")
        token = authenticate()

        logging.info("Запуск ассистента по базе знаний.")
        responses = start_knowledge_base_prediction(test_cases, token)

        if responses:
            logging.info("Результаты от ассистента получены успешно.")

            logging.info("Предобработка результатов.")
            processed_results = process_results(test_cases, responses)

            # Создание уникального имени для нового листа без двоеточий
            new_sheet_name = 'Test Results ' + datetime.now().strftime('%Y-%m-%d %H-%M-%S')

            logging.info(f"Сохранение результатов в новый лист: {new_sheet_name}.")
            create_new_sheet_and_write_results(new_sheet_name, processed_results)
        else:
            logging.error("Не удалось получить результаты ассистента.")

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        logging.error("Подробности:", exc_info=True)


if __name__ == "__main__":
    run_tests()
