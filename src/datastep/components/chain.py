import os

from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain

from datastep.components.patched_database_class import SQLDatabasePatched
from datastep.components.patched_sql_chain import SQLDatabaseChainPatched

load_dotenv()


def get_db(tables: list[str] = None) -> SQLDatabasePatched:
    # Создаём подключение к БД
    # include_tables используем для указания таблиц, с которыми хотим работать
    return SQLDatabasePatched.from_uri(
        os.getenv("DB_URI"),
        include_tables=tables,
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
    prompt: PromptTemplate
) -> SQLDatabaseChain:
    # Создаём цепочку для работы с SQL
    # use_query_checker используем для обработки неправильно составленных SQL запросов
    # use_query_checker=False, потому что True с моделью на 16К токенов ломает чейн
    # Используем кастомный промпт, чтобы указать в нём особенности нашей таблицы
    return SQLDatabaseChainPatched.from_llm(
        llm=llm,
        db=db,
        prompt=prompt,
        use_query_checker=False,
        return_direct=False,
        return_intermediate_steps=True
    )
