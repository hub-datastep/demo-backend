from datetime import datetime

from loguru import logger

from services.auth_api_service import authenticate
from services.google_sheets_service import create_new_offline_sheet_and_write_results, get_test_cases
from services.mapping_api_service import start_nomenclature_mapping, wait_for_job_completion
from utils.result_mapper import process_results


def run_tests():
    logger.info("Получение тест кейсов.")
    test_cases = get_test_cases()
    test_cases_count = len(test_cases)
    logger.info(f"Test cases count: {test_cases_count}")

    logger.info("Авторизация в API.")
    token = authenticate()

    logger.info("Запуск маппинга номенклатур.")
    job_id = start_nomenclature_mapping(test_cases, token)

    if job_id:
        logger.info(f"Job ID: {job_id}")
        logger.info("Ожидание завершения задачи маппинга.")

        # Одна номенклатура обрабатывается примерно 15-30 секунд
        # Поэтому рассчитываем время получения результата
        # относительно кол-ва номенклатур
        # Фетчим результат каждые примерно 50 номенклатур
        result_fetch_interval = test_cases_count / 50 * 30
        # result_fetch_interval = 30

        # Ожидание завершения задачи
        result = wait_for_job_completion(job_id, token, interval=result_fetch_interval)
        logger.info(f"Mapping results count: {len(result)}")

        if result:
            logger.info("Результаты маппинга получены успешно.")
            logger.info(result)

            logger.info("Предобработка результатов.")
            processed_results = process_results(test_cases, result)

            # Создание уникального имени для нового листа без двоеточий
            tests_datetime = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            new_sheet_name = f"Mapping Results {tests_datetime}"

            logger.info(f"Сохранение результатов в новый лист: {new_sheet_name}.")
            create_new_offline_sheet_and_write_results(new_sheet_name, processed_results)
        else:
            logger.error("Не удалось получить результаты маппинга.")


if __name__ == "__main__":
    run_tests()
