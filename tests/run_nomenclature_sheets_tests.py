import logging
import pprint
from datetime import datetime

from services.auth_api_service import authenticate
from services.google_sheets_service import create_new_offline_sheet_and_write_results, get_test_cases
from services.mapping_api_service import start_nomenclature_mapping, wait_for_job_completion
from utils.result_mapper import process_results

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_tests():
    try:
        logging.info("Получение тест кейсов.")
        test_cases = get_test_cases()
        print(f"Test cases count: {len(test_cases)}")

        logging.info("Авторизация в API.")
        token = authenticate()

        logging.info("Запуск маппинга номенклатур.")
        job_id = start_nomenclature_mapping(test_cases, token)

        if job_id:
            logging.info(f"Job ID: {job_id}")
            logging.info("Ожидание завершения задачи маппинга.")
            # Ожидание завершения задачи
            result = wait_for_job_completion(job_id, token, interval=30)
            print(f"Mapping results count: {len(result)}")

            if result:
                logging.info("Результаты маппинга получены успешно.")
                pprint.pprint(result)

                logging.info("Предобработка результатов.")
                processed_results = process_results(test_cases, result)

                # Создание уникального имени для нового листа без двоеточий
                new_sheet_name = f"Mapping Results {datetime.now().strftime('%Y-%m-%d %H-%M-%S')}"

                logging.info(f"Сохранение результатов в новый лист: {new_sheet_name}.")
                create_new_offline_sheet_and_write_results(new_sheet_name, processed_results)
            else:
                logging.error("Не удалось получить результаты маппинга.")
        else:
            logging.error("Не удалось запустить маппинг номенклатур.")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        logging.error("Подробности:", exc_info=True)


if __name__ == "__main__":
    run_tests()
