import asyncio
import pandas as pd

from datastep.components.datastep_sql_database import DatastepSqlDatabase
from datastep.datastep_chains.datastep_check_data_chain import check_data
from datastep.datastep_chains.datastep_similar_queries import generate_similar_queries
from datastep.datastep_chains.datastep_sql_chain import DatastepSqlChain

from dto.datastep_prediction_dto import DatastepPredictionDto, DatastepPredictionOutDto
from dto.query_dto import QueryDto
from dto.config_dto import PredictionConfigDto
from repository.prompt_repository import prompt_repository
from repository.tenant_repository import tenant_repository


async def datastep_get_prediction(body: QueryDto, tenant_id: int, prediction_config: PredictionConfigDto) -> DatastepPredictionDto:
    tenant_db_uri = tenant_repository.get_db_uri_by_tenant_id(tenant_id)
    tenant_active_prompt_template = prompt_repository.get_active_prompt_by_tenant_id(tenant_id, body.tables[0])

    datastep_sql_database = DatastepSqlDatabase(
        database_connection_string=tenant_db_uri,
        include_tables=body.tables,
        tenant_id=tenant_id
    )

    datastep_sql_chain = DatastepSqlChain(
        sql_database=datastep_sql_database.database,
        prompt_template=tenant_active_prompt_template.prompt,
        verbose=False
    )

    functions = []

    if prediction_config.is_data_check:
        functions.append(check_data(body.query, datastep_sql_database))
    if prediction_config.is_alternative_questions:
        functions.append(generate_similar_queries(body.query, datastep_sql_database))

    results = await asyncio.gather(
        *functions,
        datastep_sql_chain.run(
            input=body.query,
            limit=body.limit, 
            is_sql_description=prediction_config.is_sql_description
        ),
    )
    result, description, alternative_queries = results[0]
    similar_queries = results[1]
    sql_query, sql_description = results[2]
    if result.lower() == "нет":
        return DatastepPredictionOutDto(
            answer=description,
            sql="",
            table="",
            table_source="",
            similar_queries=alternative_queries
        )

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
