from config.config import config
from datastep.components.chain import get_db, get_llm
from datastep.components.sql_database_chain_executor import get_sql_database_chain_executor
from datastep.utils.supabase_repository import supabase_repository
from datastep.models.test import Test
from datastep.models.test_set import TestSet


TEST_SET_NAME = "all_tables-employees_questions-07.09.23"
TEST_SET_DESCRIPTION = "Тестируем версию 0.0.2 ассистента по сотрудникам"
CREATED_BY = "bleschunov"
QUESTIONS_FILE_PATH = "../data/employees_questions.txt"
TABLE_NAMES = ["employees"]


datastep_service = get_sql_database_chain_executor(
    get_db(),
    get_llm(model_name="gpt-3.5-turbo-16k"),
    debug=False,
    verbose_answer=config["verbose_answer"]
)


def get_questions(filename: str) -> list[str]:
    with open(f"./{filename}") as f:
        return f.read().splitlines()


def display_current_progress(current_question_number: int, questions_count: int) -> None:
    # Печатает, сколько процентов вопросов обработано
    print(str(round(current_question_number / questions_count * 100)) + "%")


def get_test_results(question: str, test_id: int = None) -> Test:
    datastep_prediction = datastep_service.run(question)

    test = Test(
        question=question,
        answer=datastep_prediction.answer,
        sql=datastep_prediction.sql,
        table=datastep_prediction.table,
        is_exception=False,
        exception="",
        test_id=test_id
    )

    return test


if __name__ == "__main__":
    questions = get_questions(QUESTIONS_FILE_PATH)
    questions_count = len(questions)

    test_set = TestSet(
        name=TEST_SET_NAME,
        description=TEST_SET_DESCRIPTION,
        created_by=CREATED_BY
    )

    # hint: test = ('data', [{'id': 2, 'name': 'test 1', 'created_at': '2023-07-27T13:16:25.494123+00:00', 'created_by': 'bleschunov', 'description': 'First test'}])
    test, count = supabase_repository.insert_test_set(test_set)
    current_test_id = test[1][0]["id"]

    for current_question_number, question in enumerate(questions):
        display_current_progress(current_question_number, questions_count)
        supabase_repository.insert_test(get_test_results(question, current_test_id))
