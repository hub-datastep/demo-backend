from langchain.prompts.prompt import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

from datastep.components.datastep_sql_database import DatastepSqlDatabase

similar_queries_template = """По данной схеме таблицы и составь 4 похожих вопроса на данный.

Вопрос:
{input}

Схема таблицы:
{table_info}

Перечисли вопросы через запятую
"""

similar_queries_prompt = PromptTemplate(
    template=similar_queries_template,
    input_variables=["table_info", "input"]
)

llm = ChatOpenAI(temperature=0.8, verbose=False, model_name="gpt-3.5-turbo")

similar_queries_chain = LLMChain(llm=llm, prompt=similar_queries_prompt, verbose=False)

database = DatastepSqlDatabase(
    database_connection_string="mssql+pyodbc://ann:!1Testtest@mssql-129364-0.cloudclusters.net:15827/DWH_Persons?driver=ODBC+Driver+17+for+SQL+Server",
    include_tables=["платежи"],
    tenant_id=1
)


def parse_similar_queries(similar_queries: str) -> list[str]:
    return [q[3:] for q in similar_queries.split("\n")]


async def generate_similar_queries(input: str) -> list[str]:
    response = await similar_queries_chain.arun(
        input=input,
        table_info=database.database.get_table_info()
    )

    return parse_similar_queries(response)
