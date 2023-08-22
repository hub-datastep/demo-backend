import json
import logging
import pandas as pd
import langchain
import dataclasses

from langchain.callbacks import StdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain

from datastep.components.chain import get_sql_database_chain_patched
from datastep.components.patched_database_class import SQLDatabasePatched
from datastep.components.custom_memory import CustomMemory, HumanMessage, AiMessage, custom_memory
from datastep.models.intermediate_steps import IntermediateSteps

from datastep.components.chain import get_db, get_llm
from datastep.components.message import SimpleText, Table, SqlCode
from datastep.components.datastep_prediction import DatastepPredictionDto


@dataclasses.dataclass
class SQLDatabaseChainExecutor:
    db_chain: SQLDatabaseChain
    memory: CustomMemory
    use_memory: bool
    chain_answer: any = dataclasses.field(default_factory=dict)
    debug: bool = False
    langchain_debug: bool = False
    verbose: bool = False
    return_intermediate_steps: bool = False
    last_intermediate_steps: IntermediateSteps = None

    def __post_init__(self):
        langchain.debug = self.langchain_debug
        self.db_chain.verbose = self.verbose
        self.db_chain.return_intermediate_steps = self.return_intermediate_steps

    def run(self, query) -> DatastepPredictionDto:
        if self.use_memory:
            final_query = self.memory.get_memory() + query
        else:
            final_query = query

        callbacks = []
        if self.debug:
            callbacks.append(StdOutCallbackHandler())

        try:
            if self.return_intermediate_steps:
                db_chain_response = self.db_chain(final_query, callbacks=callbacks)
                chain_answer = db_chain_response.get("result", None)
                self.last_intermediate_steps = IntermediateSteps.from_chain_steps(
                    db_chain_response.get("intermediate_steps", None)
                )
            else:
                chain_answer = self.db_chain.run(
                    final_query,
                    callbacks=callbacks
                )
        except Exception as e:
            logging.error(e)
            chain_answer = "Произошла ошибка"

        if self.debug:
            print("Final query:\n" + final_query)
            print("\n=====\n")
            print(f"Chat history size: {self.get_chat_history_size()} tokens")
            print("\n=====\n")
            print("Final answer:\n" + chain_answer)
            print("\n=====\n")

        self.memory.add_message(HumanMessage(query)).add_message(
            AiMessage(chain_answer)
        )
        try:
            self.chain_answer = json.loads(chain_answer)
        except json.JSONDecodeError:
            self.chain_answer = {
                "Answer": chain_answer if isinstance(chain_answer, str) else None
            }

        answer = self.get_answer()
        intermediate_steps = self.get_last_intermediate_steps()
        df = self.get_df()

        return DatastepPredictionDto(
            answer=SimpleText(answer).get(),
            sql=SqlCode(intermediate_steps.sql_query).get(),
            table=Table(df).get(),
        )

    def get_answer(self) -> str:
        if isinstance(self.chain_answer, dict):
            return str(self.chain_answer.get("Answer"))
        else:
            return self.chain_answer

    def get_sql(self) -> str:
        return self.get_last_intermediate_steps().sql_result

    def get_df(self) -> pd.DataFrame | None:
        steps = self.get_last_intermediate_steps()
        df = pd.DataFrame(
            steps.sql_result,
            columns=steps.sql_result[0].keys() if steps.sql_result else None,
        )

        return df

    def get_all(self) -> tuple[str, pd.DataFrame | None]:
        return self.get_answer(), self.get_df()

    def get_chat_history_size(self) -> int:
        return self.db_chain.llm_chain.llm.get_num_tokens(self.memory.get_memory())

    def get_last_intermediate_steps(self) -> IntermediateSteps:
        return self.last_intermediate_steps

    def reset(self) -> None:
        self.memory.reset()


def get_sql_database_chain_executor(
    db: SQLDatabasePatched,
    llm: ChatOpenAI,
    use_memory: bool = True,
    debug: bool = False,
) -> SQLDatabaseChainExecutor:
    return SQLDatabaseChainExecutor(
        get_sql_database_chain_patched(db, llm),
        custom_memory,
        use_memory,
        debug=debug,
        return_intermediate_steps=True
    )


def get_datastep(table_names: list[str] | None, model_name: str | None = "gpt-3.5-turbo-16k"):
    if table_names is None:
        table_names = ["test"]

    return get_sql_database_chain_executor(
        get_db(tables=table_names),
        get_llm(model_name=model_name),
        debug=True,
    )