from langchain.chains import LLMChain
from langchain.prompts.prompt import PromptTemplate
from langchain_openai import AzureChatOpenAI

from infra.env import env
from llm.component.sql_database import DatastepSqlDatabase
from util.logger import async_log

similar_queries_template = """
По данной схеме таблицы и составь 4 похожих вопроса на данный.

Вопрос:
{query}

Схема таблицы:
{table_info}

Перечисли вопросы через запятую
"""


def get_chain():
    similar_queries_prompt = PromptTemplate(
        template=similar_queries_template,
        input_variables=["query", "table_info"]
    )
    llm = AzureChatOpenAI(
        deployment_name=env.AZURE_DEPLOYMENT_NAME_SIMILAR_QUERIES,
        temperature=0.8,
        verbose=False,
    )
    similar_queries_chain = LLMChain(llm=llm, prompt=similar_queries_prompt, verbose=False)
    return similar_queries_chain


def parse_similar_queries(similar_queries: str) -> list[str]:
    return [q[3:] for q in similar_queries.split("\n")]


@async_log("Генерация похожих вопросов")
async def generate_similar_queries(
    query: str,
    database: DatastepSqlDatabase, turn_on: bool,
) -> list[str]:
    if not turn_on:
        return []

    similar_queries_chain = get_chain()
    response = await similar_queries_chain.arun(
        query=query,
        table_info=database.database.get_table_info()
    )

    return parse_similar_queries(response)
