import random

from dto.question_dto import QuestionDto
from infra.supabase import supabase


class QuestionsRepository:
    @classmethod
    def get_questions(cls, limit: int) -> list[QuestionDto]:
        (_, questionsList), _ = supabase\
            .table("template_questions")\
            .select("*")\
            .execute()
        questionsList = random.choices(questionsList, k=limit)

        return [QuestionDto(**questionItem) for questionItem in questionsList]


questions_repository = QuestionsRepository()
