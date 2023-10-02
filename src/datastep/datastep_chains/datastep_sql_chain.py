from collections import namedtuple
from collections.abc import Coroutine

from langchain.utilities import SQLDatabase
from langchain.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain.chains.sql_database.prompt import SQL_PROMPTS
from langchain.chains import LLMChain
from langchain_experimental.sql.base import PROMPT
from langchain.prompts.prompt import PromptTemplate


datastep_sql_chain_template = """You are a MS SQL expert. Given an input question, create a syntactically correct MS SQL query to run. Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.
Unless the user specifies in his question a specific number of examples he wishes to obtain, always limit your query to at most 5 results using the TOP clause as per MS SQL.
You MUST show only MS SQL query.

Only use the following tables:
{table_info}

Question: {input}"""


class DatastepSqlChain:
    def __init__(
        self,
        sql_database: SQLDatabase,
        temperature: int = 0,
        verbose: bool = False
    ):
        self.sql_database = sql_database

        llm = ChatOpenAI(temperature=temperature, verbose=verbose, model_name="gpt-3.5-turbo")

        datastep_sql_chain_prompt = PromptTemplate(
            input_variables=["input", "table_info"],
            template=datastep_sql_chain_template
        )

        db_chain = LLMChain(llm=llm, prompt=datastep_sql_chain_prompt, verbose=verbose)

        self.chain = db_chain

    async def arun(self, input: str) -> str:
        table_info = self.sql_database.get_table_info()
        return await self.chain.arun(input=input, table_info=table_info)
