from langchain.chains import LLMChain
from langchain.prompts.prompt import PromptTemplate
from langchain_openai import AzureChatOpenAI

from infra.env import AZURE_DEPLOYMENT_NAME_DB_ASSISTANT
from util.logger import async_log

sql2text_template = """
Объясни SQL запрос для топ–менеджера, который не знает, что такое SQL. Не показывай SQL.
Уложиcь в 5 предложений.

SQL запрос:
{input}

Используй формат в виде нумерованного списка.
"""

sql2text_prompt = PromptTemplate(
    template=sql2text_template,
    input_variables=["input"]
)

# llm = ChatOpenAI(
#     model_name=DB_MODEL_NAME,
#     openai_api_base=OPENAI_API_BASE,
#     temperature=0,
#     verbose=False,
# )
llm = AzureChatOpenAI(
    azure_deployment=AZURE_DEPLOYMENT_NAME_DB_ASSISTANT,
    temperature=0,
    verbose=False,
)

sql2text_chain = LLMChain(llm=llm, prompt=sql2text_prompt, verbose=False)


@async_log("Генерация описания SQL")
async def describe_sql(sql: str) -> str:
    response = await sql2text_chain.arun(sql)
    return response
