import pandas as pd

from datastep.components.datastep_sql_database import DatastepSqlDatabase
from datastep.datastep_chains.datastep_markdown_chain import DatastepMarkdownChain
from datastep.datastep_chains.datastep_sql_chain import DatastepSqlChain
from dto.datastep_prediction_dto import DatastepPredictionDto
from dto.query_dto import QueryDto
from repository.prompt_repository import prompt_repository
from repository.tenant_repository import tenant_repository


async def datastep_get_prediction(body: QueryDto, tenant_id: int) -> DatastepPredictionDto:
    tenant_db_uri = tenant_repository.get_db_uri_by_id(tenant_id)
    tenant_active_prompt_template = prompt_repository.get_active_prompt_by_tenant_id(tenant_id)

    datastep_sql_database = DatastepSqlDatabase(
        database_connection_string=tenant_db_uri,
        include_tables=body.tables
    )
    datastep_sql_chain = DatastepSqlChain(
        sql_database=datastep_sql_database.database,
        prompt_template=tenant_active_prompt_template
    )
    # TODO: Можно ли без него обойтись
    datastep_markdown_chain = DatastepMarkdownChain()

    sql_query = await datastep_sql_chain.arun(body.query)
    # TODO: разобраться, как сделать подключение к базе асинк
    sql_query_result = datastep_sql_database.run(sql_query)
    sql_query_result_markdown = await datastep_markdown_chain.arun(str(sql_query_result))
    sql_query_result_table_source = pd.DataFrame(sql_query_result)\
        .to_json(orient="table", force_ascii=False, index=False)

    return DatastepPredictionDto(
        answer="",
        sql=sql_query,
        table=sql_query_result_markdown,
        table_source=sql_query_result_table_source
    )
