from datastep.utils.logger import logging
from datastep.components.chain import get_db, get_llm
from datastep.components.sql_database_chain_executor import get_sql_database_chain_executor


def get_questions(filename: str) -> list[str]:
    with open(f"./{filename}") as f:
        return f.read().splitlines()


def print_current_progress(current_question_number: int, questions_count: int) -> None:
    # Печатает, сколько процентов вопросов обработано
    print(str(round(current_question_number / questions_count * 100)) + "%")


datastep_service = get_sql_database_chain_executor(
    get_db(tables=["УСО БДДС - С начала 2022 года - ПЗЕ"]),
    get_llm(model_name="gpt-3.5-turbo-16k"),
    debug=True
)

questions = get_questions("../data/questions.txt")

for i, q in enumerate(questions):
    print_current_progress(i, len(questions))
    result = datastep_service.run(q)

    if not result.is_exception:
        logging.info(f"[Query][{q}][Answer][{result.answer}][SQL][{result.sql}]")
    else:
        logging.error(f"[Query][{q}][Answer][{result.answer}][SQL][{result.sql}]")
