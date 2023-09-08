from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain.tools import Tool, StructuredTool
from langchain import OpenAI

from config.config import config
from datastep.components.chain import get_db, get_llm, get_sql_database_chain_patched
from datastep.components.datastep_prompt import datastep_prompt
from datastep.components.datastep_memory_chain import datastep_memory_chain
from datastep.components.sql_database_chain_executor import get_sql_database_chain_executor

# db = get_db(config["db_uri"], tables=config["tables"])
# llm = get_llm(model_name="gpt-3.5-turbo-16k")
#
# datastep_database_chain = get_sql_database_chain_patched(
#     db,
#     llm,
#     datastep_prompt.get_prompt(),
#     verbose_answer=False
# )

datastep_service = get_sql_database_chain_executor(
    get_db(config["db_uri"], tables=config["tables"]),
    get_llm(model_name="gpt-3.5-turbo-16k"),
    debug=True,
    verbose_answer=config["verbose_answer"]
)

tools = [
    Tool(
        name="sql_database",
        func=datastep_service.run,
        description="useful for when there are not enough data in chat history",
    ),
    Tool(
        name="conversation_chain",
        func=datastep_memory_chain.run,
        description="useful for when you want to answer question",
    ),
]

agent = initialize_agent(
    tools=tools,
    llm=OpenAI(model_name="gpt-3.5-turbo-16k"),
    verbose=True
)

print(agent.run("Кто из них заработал больше всего? Дай ответ по истории"))
