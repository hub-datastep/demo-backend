from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.callbacks.arize_callback import ArizeCallbackHandler

from config.config import config
from datastep.components.datastep_prediction import DatastepPrediction
from datastep.components.datastep_prompt import DatastepPrompt
from repository.prompt_repository import PromptRepository
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks import StdOutCallbackHandler

arize_callback = ArizeCallbackHandler(
    model_id="datastep",
    model_version="1.0",
    SPACE_KEY="ad4e321",
    API_KEY="4b4a463031c9906fe45"
)

manager = CallbackManager([StdOutCallbackHandler(), arize_callback])


sql_llm = ChatOpenAI(temperature=0, model_name="gpt-4")
agent_llm = ChatOpenAI(temperature=0, model_name="gpt-4", callback_manager=manager)

db = SQLDatabase.from_uri(config["db_uri"], include_tables=config["tables"], view_support=True)

table_description = PromptRepository.fetch_by_id(config["prompt_id"])
db_chain = SQLDatabaseChain.from_llm(
    agent_llm,
    db,
    verbose=True,
    prompt=DatastepPrompt.get_prompt(table_description.prompt)
)
db_chain.llm_chain.verbose = True

# toolkit = SQLDatabaseToolkit(db=db, llm=chat_llm)
# agent_executor = create_sql_agent(
#     llm=chat_llm,
#     toolkit=toolkit,
#     verbose=True,
#     agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
# )

# agent_executor.agent.llm_chain.verbose = True

memory = ConversationBufferWindowMemory(k=3, memory_key="chat_history", input_key='input', output_key="output")

tools = [
    Tool(
        name="Database Chain",
        description="Useful for when you need data from database",
        func=db_chain.run,
        return_direct=True,
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
    agent_llm,
    agent_kwargs={
        "format_instructions": format_instructions
    },
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
    return_intermediate_steps=True,
)


datastep_agent.agent.llm_chain.verbose = False


def execute(query: str) -> DatastepPrediction:
    try:
        response = datastep_agent(query)
        return DatastepPrediction(
            answer=response["output"],
            sql="",
            table="",
            is_exception=False,
            table_source=""
        )
    except Exception as e:
        return DatastepPrediction(
            answer=str(e),
            sql="",
            table="",
            is_exception=False,
            table_source=""
        )

out = datastep_agent("Покажи топ 5 контрагентов по доходу в базе данных")
print(out)
# out = datastep_agent("Кто из них заработал меньше всего?")
# print(out['output'])
