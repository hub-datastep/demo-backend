from dto.question_dto import QuestionDto
from service.question_service import question_service


def get_random_questions(tables: list[str], limit: int) -> list[QuestionDto]:
    return question_service.run(tables, limit)
