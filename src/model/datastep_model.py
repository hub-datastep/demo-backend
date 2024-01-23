import asyncio
from typing import Type

import pandas as pd

from datastep.components.datastep_sql_database import DatastepSqlDatabase
from datastep.datastep_chains.datastep_check_data_chain import check_data
from datastep.datastep_chains.datastep_similar_queries import generate_similar_queries
from datastep.datastep_chains.datastep_sql_chain import DatastepSqlChain
from scheme.database_prediction_config_scheme import DatabasePredictionConfig
from scheme.prediction_scheme import DatabasePredictionQuery, DatabasePredictionRead
from scheme.tenant_scheme import Tenant
from util.logger import async_log


@async_log("Получение ответа ассистента")
async def datastep_get_prediction(
    body: DatabasePredictionQuery,
    tenant: Type[Tenant],
    prediction_config: DatabasePredictionConfig | None
) -> DatabasePredictionRead:
    tenant_db_uri = tenant.db_uri
    tenant_active_prompt_template = tenant.active_prompt

    datastep_sql_database = DatastepSqlDatabase(
        database_connection_string=tenant_db_uri,
        include_tables=body.tables,
    )

    datastep_sql_chain = DatastepSqlChain(
        sql_database=datastep_sql_database.database,
        prompt_template=tenant_active_prompt_template.prompt,
        verbose=False
    )

    functions = []

    is_data_check = prediction_config is None or prediction_config.is_data_check
    functions.append(check_data(body.query, datastep_sql_database, turn_on=is_data_check))

    is_alternative_questions = prediction_config is None or prediction_config.is_alternative_questions
    functions.append(generate_similar_queries(body.query, datastep_sql_database, turn_on=is_alternative_questions))

    is_sql_description = prediction_config is None or prediction_config.is_sql_description

    results = await asyncio.gather(
        *functions,
        datastep_sql_chain.run(
            input=body.query,
            limit=body.limit, 
            is_sql_description=is_sql_description
        ),
    )
    result, description, alternative_queries = results[0]
    similar_queries = results[1]
    sql_query, sql_description = results[-1]
    if result.lower() == "нет":
        return DatabasePredictionRead(
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

    return DatabasePredictionRead(
        answer=sql_description,
        sql=f"~~~sql\n{sql_query}\n~~~",
        table=sql_query_result_markdown,
        table_source=sql_query_result_table_source,
        similar_queries=similar_queries
    )
