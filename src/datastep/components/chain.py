import os

from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI

from config.config import config
from datastep.components.patched_database_class import SQLDatabasePatched
from datastep.components.patched_sql_chain import SQLDatabaseChainPatched
from datastep.components.questions.patched_question_chain import \
    QuestionChainPatched

load_dotenv()


def get_db() -> SQLDatabasePatched:
    # Создаём подключение к БД
    # include_tables используем для указания таблиц, с которыми хотим работать
    return SQLDatabasePatched.from_uri(
        config["db_uri"] or os.getenv("DB_URI"),
        include_tables=config["tables"],
        view_support=True,
    )


def get_llm(model_name: str = "gpt-3.5-turbo-16k") -> ChatOpenAI:
    # Создаём ЛЛМ–модель для работы цепочки для работы с SQL
    return ChatOpenAI(
        temperature=0,
        verbose=False,
        max_tokens=None,
        model_name=model_name
    )


def get_sql_database_chain_patched(
    db: SQLDatabasePatched,
    llm: ChatOpenAI,
    prompt: PromptTemplate,
    verbose_answer: bool = False
) -> SQLDatabaseChainPatched:
    # Создаём цепочку для работы с SQL
    # use_query_checker используем для обработки неправильно составленных SQL запросов
    # use_query_checker=False, потому что True с моделью на 16К токенов ломает чейн
    # Используем кастомный промпт, чтобы указать в нём особенности нашей таблицы
    return SQLDatabaseChainPatched.from_llm(
        llm=llm,
        db=db,
        prompt=prompt,
        use_query_checker=False,
        return_direct=not verbose_answer,
        return_intermediate_steps=True
    )


def get_question_chain_patched(
    llm: ChatOpenAI,
    prompt: PromptTemplate,
) -> QuestionChainPatched:
    return QuestionChainPatched(
        llm=llm,
        prompt=prompt,
        return_intermediate_steps=True
    )
