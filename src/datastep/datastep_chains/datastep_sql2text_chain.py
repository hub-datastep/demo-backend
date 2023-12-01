import asyncio

# from langchain.callbacks import AsyncIteratorCallbackHandler
# from langchain.callbacks import I
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

from util.logger import async_log

from dotenv import load_dotenv

load_dotenv()

sql2text_template = """Объясни SQL запрос для топ–менеджера, который не знает, что такое SQL. Не показывай SQL. Уложиcь в 5 предложений

SQL запрос:
{input}

Используй формат в виде нумерованного списка
"""

sql2text_prompt = PromptTemplate(
    template=sql2text_template,
    input_variables=["input"]
)

# callback = BaseCallbackHandler()
llm = ChatOpenAI(
    temperature=0,
    verbose=False,
    model_name="gpt-4",
    streaming=True,
    # callbacks=[callback]
)

# sql2text_chain = LLMChain(llm=llm, prompt=sql2text_prompt, verbose=False)
sql2text_chain = sql2text_prompt | llm
# @async_log("Генерация описания SQL")
# async def describe_sql(sql: str) -> str:
#     response = await sql2text_chain.arun(sql)
#     return response


@async_log("Генерация описания SQL")
def describe_sql_stream(sql: str):
    for chunk in sql2text_chain.stream({"input": sql}):
        yield chunk.content


# async def test():
#     async for chunk in describe_sql_stream(
#         "SELECT TOP 5 [Контрагент] AS Company FROM [платежи] WHERE [План / Факт] = 'Факт' GROUP BY [Контрагент] ORDER BY SUM([Сумма]) DESC"
#     ):
#         print(chunk, end="", flush=True)

# asyncio.run(
# test()
# for chunk in describe_sql_stream(
#     "SELECT TOP 5 [Контрагент] AS Company FROM [платежи] WHERE [План / Факт] = 'Факт' GROUP BY [Контрагент] ORDER BY SUM([Сумма]) DESC"
# ):
#     print(chunk, end="", flush=True)
# )

# resp = llm.stream("SELECT TOP 5 [Контрагент] AS Company FROM [платежи] WHERE [План / Факт] = 'Факт' GROUP BY [Контрагент] ORDER BY SUM([Сумма]) DESC")
# for chunk in resp:
#     print(chunk.content, end="", flush=True)

