import dataclasses

import langchain
from dotenv import load_dotenv
from langchain.callbacks import StdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from openai import OpenAIError
from sqlalchemy.exc import SQLAlchemyError

from datastep.components.chain import get_question_chain_patched
from datastep.components.questions.patched_question_chain import \
    QuestionChainPatched
from datastep.components.questions.question_prompt import QuestionPrompt
from dto.question_dto import QuestionDto
from repository.prompt_repository import prompt_repository

load_dotenv()

# TODO: add prompt for "Сотрудники"
TABLE_PROMPT_ID_MAPPING = {
    "платежи": 4,
}


@dataclasses.dataclass
class QuestionChainExecutor:
    question_chain: QuestionChainPatched
    debug: bool = False
    verbose_answer: bool = False
    langchain_debug: bool = False

    def __post_init__(self):
        langchain.debug = self.langchain_debug

    def run(self, tables: list[str], limit: int) -> list[QuestionDto]:
        if tables:
            prompt_dto = prompt_repository.fetch_by_id(TABLE_PROMPT_ID_MAPPING[tables[0]])
        else:
            # Prompt with id == 4 - default prompt with just table description
            prompt_dto = prompt_repository.fetch_by_id(4)

        self.question_chain.prompt = QuestionPrompt.get_prompt(
            table_description=prompt_dto.prompt,
            limit=limit
        )

        try:
            question_chain_response = self.question_chain._ideate()
        except OpenAIError as e:
            print(e)
        except SQLAlchemyError as e:
            print(e)

        chain_answer = question_chain_response.split("\n")

        return [QuestionDto(question=question) for question in chain_answer]

    def get_callbacks(self):
        callbacks = []
        if self.debug:
            callbacks.append(StdOutCallbackHandler())

        return callbacks


def get_question_chain_executor(
    llm: ChatOpenAI,
    debug: bool = True,
    verbose_answer: bool = False
) -> QuestionChainExecutor:
    return QuestionChainExecutor(
        question_chain=get_question_chain_patched(
            llm=llm,
            prompt=QuestionPrompt.get_prompt(),
        ),
        debug=debug,
        verbose_answer=verbose_answer
    )
