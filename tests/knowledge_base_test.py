from loguru import logger

from configs.env import env
from services.api.kb_service import start_knowledge_base_prediction
from services.google_sheets_service import get_test_cases, save_results_locally
from utils.result_knowledge_base import process_results

_RESULTS_SHEET_NAME = "Knowledge Base Results"


def run_tests():
    logger.info("Getting Test Cases..")
    test_cases_list = get_test_cases(
        spreadsheet_name=env.TESTS_SPREADSHEET_NAME,
        sheet_name=env.TESTS_TABLE_NAME,
    )
    logger.info(f"Test Cases count: {len(test_cases_list)}")

    logger.info("Starting Tests..")
    results = start_knowledge_base_prediction(test_cases=test_cases_list)

    logger.info(f"Results count: {len(results)}")
    # logger.info(results)

    logger.info("Processing results..")
    processed_results = process_results(
        test_cases=test_cases_list,
        api_results=results,
    )

    save_results_locally(
        new_sheet_name=_RESULTS_SHEET_NAME,
        processed_results=processed_results,
    )


if __name__ == "__main__":
    run_tests()
