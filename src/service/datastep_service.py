from datastep.components.chain import get_db, get_llm
from datastep.components.sql_database_chain_executor import get_sql_database_chain_executor

datastep_service = get_sql_database_chain_executor(
    get_db(tables=["УСО БДДС - С начала 2022 года - ПЗЕ"]),
    get_llm(model_name="gpt-3.5-turbo-16k"),
    use_memory=False,
    debug=False,
)
