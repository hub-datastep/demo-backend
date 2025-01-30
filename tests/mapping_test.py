from loguru import logger

from configs.env import env
from services.api.mapping_service import start_mapping, wait_for_job_completion
from services.google_sheets_service import get_test_cases, save_results_locally
from utils.mapping_results import process_results

_RESULTS_SHEET_NAME = "Mapping Results"


def run_tests():
    logger.info("Getting Test Cases..")
    test_cases_list = get_test_cases(
        spreadsheet_name=env.TESTS_SPREADSHEET_NAME,
        sheet_name=env.TESTS_TABLE_NAME,
    )
    test_cases_count = len(test_cases_list)
    logger.info(f"Test Cases count: {test_cases_count}")

    logger.info("Starting Tests..")
    job = start_mapping(test_cases=test_cases_list)

    job_id = job.job_id
    logger.info(f"Job ID: {job_id}")

    # Одна номенклатура обрабатывается примерно 15-30 секунд
    # Поэтому рассчитываем время получения результата
    # относительно кол-ва номенклатур
    # Фетчим результат примерно каждые 50 номенклатур
    fetch_interval = test_cases_count / 50 * 30

    logger.info("Wait until job finished..")
    results = wait_for_job_completion(
        job_id=job_id,
        interval=fetch_interval,
    )

    if not results:
        logger.error("Cannot get results.")

    logger.info(f"Results count: {len(results)}")
    # logger.info(results)

    logger.info("Processing results..")
    processed_results = process_results(
        test_cases=test_cases_list,
        results=results,
    )

    save_results_locally(
        new_sheet_name=_RESULTS_SHEET_NAME,
        processed_results=processed_results,
    )


if __name__ == "__main__":
    run_tests()
