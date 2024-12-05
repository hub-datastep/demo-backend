import os
from datetime import datetime

from dotenv import load_dotenv
from loguru import logger
from pandas import DataFrame
from tqdm import tqdm

from datastep.chains.order_multi_classification.order_multi_classification_chain import get_order_class
from google_sheets_service import read_sheet

load_dotenv()

TESTS_ORDER_CLASSIFICATION_SPREADSHEET_NAME = os.getenv('TESTS_ORDER_CLASSIFICATION_SPREADSHEET_NAME')
TESTS_ORDER_CLASSIFICATION_TABLE_NAME = os.getenv('TESTS_ORDER_CLASSIFICATION_TABLE_NAME')

RULES_BY_CLASS = {
    "Клининг": [
        "Требуется уборка",
        "Упоминание загрязнений"
    ],
    "Охрана": [
        "Выдача пропуска на въезд/для автомобиля",
        "Нарушение общественного порядка",
        "Ломятся в квартиру",
        "Шум от соседей (не считается шум от каких-либо приборов и установок в доме)",
        "Проблемы и конфликты на парковке"
    ],
    "Домофон": [
        "Не работает домофон или работает плохо",
        "Не работает ключ от домофона или работает плохо"
    ],
    "Аварийная": [
        "Все заявки, связанные с неисправностью лифтов, считаются аварийными, за исключением консультаций и вопросов по внутреннему убранству кабины",
        "Протечки считаются аварийной ситуацией, если они происходят не из-за каких-либо погодных условий",
        "Части систем отопления и водоснабжения, например когда нет холодной или горячей воды, это считается аварийной ситуацией",
        "В тексте указана любая критическая поломка, которая негативно влияет одновременно на большое количество людей или несёт угрозу жизни или имуществу"
    ],
    "Обычная": [
        "Проблемы с водоснабжением на уровне квартир, если проблема исключительно в счетчиках",
        "Неисправность в зоне ответственности собственника, например неисправен смеситель и он не закрывается",
        "Заявки по внутренним системам управления, если они поступают не от жителей",
        "Внутренние заявки, заводимые и закрываемые сотрудниками аварийной диспетчерской, которые поступают не от жителей, например: 'Мониторинг БМС', 'Проверка связи АПС'"
    ]
}


def _get_test_cases():
    return read_sheet(
        TESTS_ORDER_CLASSIFICATION_SPREADSHEET_NAME,
        TESTS_ORDER_CLASSIFICATION_TABLE_NAME,
        None
    )


def _save_results(results_list: list):
    results_df = DataFrame(results_list)

    now_time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    new_sheet_name = f"Order Classification Results {now_time}"
    file_path = f"{new_sheet_name}.xlsx"

    results_df.to_excel(file_path, index=False)
    logger.info(f"Результаты тестов успешно сохранены: {file_path}")


if __name__ == "__main__":
    test_cases_list = _get_test_cases()[:155]

    results_list = []
    for order in tqdm(test_cases_list, unit="test order"):
        start_time = datetime.now()

        order_query = order['Order Query']
        correct_class = order['Correct Class']

        order_class_response = get_order_class(
            order_query=order_query,
            rules_by_class=RULES_BY_CLASS,
            # verbose=True,
        )
        predicted_class = order_class_response.order_class
        llm_comment = order_class_response.comment

        end_time = datetime.now()
        process_time = end_time - start_time

        classified_order = {
            **order,
            "Predicted Class": f"{predicted_class}",
            "LLM Comment": f"{llm_comment}",
            "Process Time": f"{process_time}",
        }
        results_list.append(classified_order)

    _save_results(results_list)
