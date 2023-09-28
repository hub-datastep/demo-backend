from dto.question_dto import QuestionDto
from repository.questions_repository import questions_repository


def get_random_questions(limit: int) -> list[QuestionDto]:
    # TODO: replace questions_repository to chain that will generate questions
    questions_service = questions_repository

    return questions_service.get_questions(limit)
