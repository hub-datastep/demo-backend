import pandas as pd

from datastep.components.datastep_sql_database import DatastepSqlDatabase
from datastep.datastep_chains.datastep_check_data_chain import check_data
from datastep.datastep_chains.datastep_similar_queries import generate_similar_queries
from datastep.datastep_chains.datastep_sql2text_chain import describe_sql
from datastep.datastep_chains.datastep_sql_chain import DatastepSqlChain
from dto.datastep_prediction_dto import DatastepPredictionDto, DatastepPredictionOutDto
from dto.query_dto import QueryDto
from repository.prompt_repository import prompt_repository
from repository.tenant_repository import tenant_repository


async def datastep_get_prediction(body: QueryDto, tenant_id: int) -> DatastepPredictionDto:
    tenant_db_uri = tenant_repository.get_db_uri_by_tenant_id(tenant_id)

    if body.tables[0] == "платежи":
        tenant_active_prompt_template = prompt_repository.fetch_by_id(1)
    else:
        tenant_active_prompt_template = prompt_repository.fetch_by_id(2)

    datastep_sql_database = DatastepSqlDatabase(
        database_connection_string=tenant_db_uri,
        include_tables=body.tables,
        tenant_id=tenant_id
    )
    datastep_sql_chain = DatastepSqlChain(
        sql_database=datastep_sql_database.database,
        prompt_template=tenant_active_prompt_template.prompt,
        verbose=True
    )

    result, description, alternative_queries = await check_data(body.query, datastep_sql_database)
    if result.lower() == "нет":
        return DatastepPredictionOutDto(
            answer=description,
            sql="",
            table="",
            table_source="",
            similar_queries=alternative_queries
        )

    similar_queries = await generate_similar_queries(body.query, datastep_sql_database)
    sql_query = await datastep_sql_chain.arun(input=body.query, limit=body.limit)
    sql_description = await describe_sql(sql_query)
    # TODO: разобраться, как сделать подключение к базе асинк
    sql_query_result = datastep_sql_database.run(sql_query)
    sql_query_result_markdown = pd.DataFrame(sql_query_result).to_markdown(index=False, floatfmt=".3f")
    sql_query_result_table_source = pd.DataFrame(sql_query_result)\
        .to_json(orient="table", force_ascii=False, index=False)

    return DatastepPredictionOutDto(
        answer=sql_description,
        sql=f"~~~sql\n{sql_query}\n~~~",
        table=sql_query_result_markdown,
        table_source=sql_query_result_table_source,
        similar_queries=similar_queries
    )
