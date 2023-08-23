import pandas as pd
import langchain
import dataclasses

from dotenv import load_dotenv
from langchain.callbacks import StdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain

from datastep.components.chain import get_sql_database_chain_patched
from datastep.components.custom_prompt import custom_prompt
from datastep.components.patched_database_class import SQLDatabasePatched
from datastep.models.intermediate_steps import IntermediateSteps
from datastep.utils.logger import logging

from datastep.components.chain import get_db, get_llm
from datastep.components.datastep_prediction import DatastepPredictionDto


load_dotenv()


@dataclasses.dataclass
class SQLDatabaseChainExecutor:
    db_chain: SQLDatabaseChain
    chain_answer: str | None = ""
    debug: bool = False
    verbose: bool = False
    langchain_debug: bool = False
    last_intermediate_steps: IntermediateSteps = None

    def __post_init__(self):
        langchain.debug = self.langchain_debug

    def run(self, query) -> DatastepPredictionDto:
        callbacks = self.get_callbacks()

        try:
            db_chain_response = self.db_chain(query, callbacks=callbacks)
            self.chain_answer = db_chain_response["result"]
            self.last_intermediate_steps = IntermediateSteps.from_chain_steps(
                db_chain_response["intermediate_steps"]
            )
        except Exception as e:
            self.chain_answer = str(e)

        if self.debug:
            self.print_logs(query)

        return self.get_datastep_prediction_dto()

    def get_datastep_prediction_dto(self):
        return DatastepPredictionDto(
            answer=self.get_answer(),
            sql=self.get_sql_markdown(),
            table=self.get_table_markdown()
        )

    def get_answer(self) -> str:
        return self.chain_answer

    def get_sql_markdown(self) -> str:
        sql_result = self.last_intermediate_steps.sql_result
        if sql_result:
            return f"~~~sql\n{sql_result}\n~~~"
        return ""

    def get_table_markdown(self) -> str:
        sql_result = self.last_intermediate_steps.sql_result
        data_frame = pd.DataFrame(sql_result)

        if data_frame is not None and any(data_frame):
            return data_frame.to_markdown(index=False, floatfmt=".3f")

        return ""

    def get_callbacks(self):
        callbacks = []
        if self.verbose:
            callbacks.append(StdOutCallbackHandler())

        return callbacks

    def print_logs(self, query):
        logging.info("Final query:\n" + query)
        logging.info("Final answer:\n" + self.chain_answer)


def get_sql_database_chain_executor(
    db: SQLDatabasePatched,
    llm: ChatOpenAI,
    debug: bool = False,
) -> SQLDatabaseChainExecutor:
    return SQLDatabaseChainExecutor(
        db_chain=get_sql_database_chain_patched(db, llm, custom_prompt),
        debug=debug,
    )
