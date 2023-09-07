from config.config import config
from datastep.components.chain import get_db, get_llm
from datastep.components.sql_database_chain_executor import get_sql_database_chain_executor

datastep_service = get_sql_database_chain_executor(
    get_db(config["db_uri"], tables=config["tables"]),
    get_llm(model_name="gpt-3.5-turbo-16k"),
    debug=True,
    verbose_answer=config["verbose_answer"]
)
