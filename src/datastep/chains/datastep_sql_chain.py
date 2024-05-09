import datetime
import re

from langchain.chains import LLMChain
from langchain.prompts.prompt import PromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_openai import AzureChatOpenAI

from datastep.chains.datastep_sql2text_chain import describe_sql
from infra.env import AZURE_DEPLOYMENT_NAME_DB_ASSISTANT
from util.logger import async_log

datastep_sql_chain_template = """
You must follow the steps described below:

Step 1:
Write down how you can change some words in the question so that it is interpreted unambiguously.
Pay attention that some words can be perceived differently, Get rid of such ambiguity.
Show the corrected question and remember it.

Question: {query}


Step 2:
Write down what types of data are needed to answer new question from Step 1?
For example, geography, physical properties, numerical values, and so on.
Give examples from the question and remember them.


Step 3:
According to this scheme, determine in the table whether all the data types from the previous answer are in the table?

Only use the following table:
{table_info}


Step 4:
Based on the previous answer, is it possible to make an SQL query?
If it is impossible, explain why?
"""


class DatastepSqlChain:
    def __init__(
        self,
        prompt_template: str,
        sql_database: SQLDatabase,
    ):
        self.sql_database = sql_database

        # llm = ChatOpenAI(
        #     openai_api_base=OPENAI_API_BASE,
        #     model_name=MODEL_NAME,
        #     temperature=temperature,
        #     verbose=verbose,
        # )
        llm = AzureChatOpenAI(
            azure_deployment=AZURE_DEPLOYMENT_NAME_DB_ASSISTANT,
            temperature=0,
            verbose=False,
        )

        datastep_sql_chain_prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["query", "table_info", "current_date", "limit"]
        )

        db_chain = LLMChain(
            llm=llm,
            prompt=datastep_sql_chain_prompt,
        )

        self.chain = db_chain

    @async_log("Генерация SQL")
    async def run(self, query: str, limit: int, is_sql_description: bool) -> (str, str):
        table_info = self.sql_database.get_table_info()
        response = await self.chain.arun(
            query=query,
            table_info=table_info,
            current_date=str(datetime.date.today()),
            limit=limit
        )
        match = re.search("SQL: (.+)", response)

        if match:
            sql_query = match.group(1)
        else:
            sql_query = response

        sql_description = ""
        if is_sql_description:
            sql_description = await describe_sql(sql_query)

        return sql_query, sql_description
