from langchain import OpenAI
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain

from config.config import config
from datastep.components.datastep_prediction import DatastepPrediction
from datastep.components.datastep_prompt import DatastepPrompt

chat_llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
llm = OpenAI(temperature=0)

db = SQLDatabase.from_uri(config["db_uri"], include_tables=config["tables"], view_support=True)

db_chain = SQLDatabaseChain.from_llm(chat_llm, db, verbose=True, prompt=DatastepPrompt.get_prompt())
db_chain.llm_chain.verbose = False

# toolkit = SQLDatabaseToolkit(db=db, llm=chat_llm)
# agent_executor = create_sql_agent(
#     llm=chat_llm,
#     toolkit=toolkit,
#     verbose=True,
#     agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
# )

# agent_executor.agent.llm_chain.verbose = True

memory = ConversationBufferMemory(memory_key="chat_history", input_key='input', output_key="output")

tools = [
    Tool(
        name="Database Chain",
        description="Useful for when you need data from database",
        func=db_chain.run
    )
]

format_instructions = """To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the Human input
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
AI: [your last observation here]
"""

datastep_agent = initialize_agent(
    tools,
    llm,
    agent_kwargs={
        "format_instructions": format_instructions
    },
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
    return_intermediate_steps=False,
)


datastep_agent.agent.llm_chain.verbose = False

def execute(query: str) -> DatastepPrediction:
    response = datastep_agent(query)
    return DatastepPrediction(
        answer=response["output"],
        sql="",
        table="",
        is_exception=False
    )

# out = datastep_agent("Топ 5 компаний по доходу")
# print(out)
# out = datastep_agent("Покажи ответ в виде таблицы")
# print(out)
