from datetime import datetime

from loguru import logger
from pandas import DataFrame
from sqlmodel import Session
from tqdm import tqdm

from configs.env import (
    TESTS_ORDER_CLASSIFICATION_SPREADSHEET_NAME,
    TESTS_ORDER_CLASSIFICATION_TABLE_NAME, TESTS_ORDER_CLASSIFICATION_CONFIG_USER_ID,
)
from infra.database import engine
from llm.chain.order_multi_classification.order_multi_classification_chain import (
    get_order_class,
)
from model.order_classification.order_classification_config_model import (
    get_order_classification_config_by_user_id
)
from model.order_classification.order_classification_model import normalize_resident_request_string
from services.google_sheets_service import read_sheet


def _get_test_cases():
    return read_sheet(
        TESTS_ORDER_CLASSIFICATION_SPREADSHEET_NAME,
        TESTS_ORDER_CLASSIFICATION_TABLE_NAME,
        None,
    )


def _save_results(results_list: list):
    results_df = DataFrame(results_list)

    now_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    new_sheet_name = f"Order Classification Results {now_time}"
    file_path = f"{new_sheet_name}.xlsx"

    results_df.to_excel(file_path, index=False)
    logger.info(f"Результаты тестов успешно сохранены: {file_path}")


if __name__ == "__main__":
    test_cases_list = _get_test_cases()
    logger.info(f"Test Cases count: {len(test_cases_list)}")

    logger.info(f"Getting config with User ID {TESTS_ORDER_CLASSIFICATION_CONFIG_USER_ID}..")
    with Session(engine) as session:
        config = get_order_classification_config_by_user_id(
            session=session,
            user_id=TESTS_ORDER_CLASSIFICATION_CONFIG_USER_ID,
        )

    rules_by_classes = config.rules_by_classes

    results_list = []
    for order in tqdm(test_cases_list, unit="test order"):
        order_query = order["Order Query"]
        correct_class = order["Correct Class"]

        if correct_class == "Другое":
            continue

        start_time = datetime.now()

        try:
            order_class_response = get_order_class(
                order_query=normalize_resident_request_string(order_query),
                rules_by_classes=rules_by_classes,
                # verbose=True,
            )
        except ValueError:
            order_id = order["Order ID"]
            logger.error(f"Order with ID {order_id} has problem with Azure Content Filter")
            continue

        predicted_class = order_class_response.most_relevant_class_response.order_class
        llm_comment = order_class_response.most_relevant_class_response.comment
        scores = order_class_response.scores
        query_summary = order_class_response.query_summary

        end_time = datetime.now()
        processing_time = end_time - start_time

        classified_order = {
            **order,
            "Query Summary": query_summary,
            "Predicted Class": predicted_class,
            "LLM Comment": llm_comment,
            "Scores": scores,
            "Processing Time": f"{processing_time}",
        }
        results_list.append(classified_order)

    _save_results(results_list)
