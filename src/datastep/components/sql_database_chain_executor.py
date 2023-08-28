import pandas as pd
import langchain
import dataclasses

from dotenv import load_dotenv
from langchain.callbacks import StdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from openai import OpenAIError
from sqlalchemy.exc import SQLAlchemyError

from datastep.components.chain import get_sql_database_chain_patched

from datastep.components.datastep_prompt import datastep_prompt
from datastep.components.patched_database_class import SQLDatabasePatched
from datastep.components.patched_sql_chain import SQLDatabaseChainPatched
from datastep.models.intermediate_steps import IntermediateSteps

from datastep.components.datastep_prediction import DatastepPrediction

load_dotenv()


@dataclasses.dataclass
class SQLDatabaseChainExecutor:
    db_chain: SQLDatabaseChainPatched
    debug: bool = False
    verbose: bool = False
    verbose_answer: bool = False
    langchain_debug: bool = False

    def __post_init__(self):
        langchain.debug = self.langchain_debug

    def run(self, query) -> DatastepPrediction:
        callbacks = self.get_callbacks()

        try:
            db_chain_response = self.db_chain(query, callbacks=callbacks)
        except OpenAIError as e:
            return DatastepPrediction(
                answer=str(e),
                sql=None,
                table=None,
                is_exception=True
            )
        except SQLAlchemyError as e:
            intermediate_steps = e.intermediate_steps
            intermediate_steps = IntermediateSteps.from_chain_steps(intermediate_steps)

            return DatastepPrediction(
                answer=str(e),
                sql=self.get_sql_markdown(intermediate_steps.sql_query),
                table=None,
                is_exception=True
            )

        if self.verbose_answer:
            chain_answer = db_chain_response["result"]
        else:
            chain_answer = ""

        intermediate_steps = db_chain_response["intermediate_steps"]
        intermediate_steps = IntermediateSteps.from_chain_steps(intermediate_steps)
        sql_query = intermediate_steps.sql_query
        sql_result = intermediate_steps.sql_result

        return DatastepPrediction(
            answer=chain_answer,
            sql=self.get_sql_markdown(sql_query),
            table=self.get_table_markdown(sql_result),
            is_exception=False
        )

    @classmethod
    def get_sql_markdown(cls, sql_result) -> str:
        if sql_result:
            return f"~~~sql\n{sql_result}\n~~~"
        return ""

    @classmethod
    def get_table_markdown(cls, sql_result) -> str:
        data_frame = pd.DataFrame(sql_result)

        if data_frame is not None and any(data_frame):
            return data_frame.to_markdown(index=False, floatfmt=".3f")

        return ""

    def get_callbacks(self):
        callbacks = []
        if self.verbose:
            callbacks.append(StdOutCallbackHandler())

        return callbacks


def get_sql_database_chain_executor(
    db: SQLDatabasePatched,
    llm: ChatOpenAI,
    debug: bool = False,
    verbose_answer: bool = False
) -> SQLDatabaseChainExecutor:
    return SQLDatabaseChainExecutor(
        db_chain=get_sql_database_chain_patched(db, llm, datastep_prompt.get_prompt(), verbose_answer),
        debug=debug,
        verbose_answer=verbose_answer
    )
