import asyncio
from typing import Type
from uuid import UUID

import pandas as pd

from datastep.chains.datastep_check_data_chain import check_data
from datastep.chains.datastep_similar_queries import generate_similar_queries
from datastep.chains.datastep_sql_chain import DatastepSqlChain
from datastep.components.sql_database import DatastepSqlDatabase
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
        schema=tenant_active_prompt_template.scheme
    )

    datastep_sql_chain = DatastepSqlChain(
        sql_database=datastep_sql_database.database,
        prompt_template=tenant_active_prompt_template.prompt,
    )

    functions = []

    is_data_check = prediction_config is None or prediction_config.is_data_check
    functions.append(check_data(body.query, datastep_sql_database, turn_on=is_data_check))

    is_alternative_questions = prediction_config is None or prediction_config.is_alternative_questions
    functions.append(generate_similar_queries(body.query, datastep_sql_database, turn_on=is_alternative_questions))

    is_sql_description = prediction_config is None or prediction_config.is_sql_description
    functions.append(datastep_sql_chain.run(body.query, body.limit, is_sql_description=is_sql_description))

    results = await asyncio.gather(*functions)
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
    sql_query = sql_query.replace("```sql", "")
    sql_query = sql_query.replace("```", "")
    sql_query_result = datastep_sql_database.run(sql_query)
    sql_query_result_markdown = pd.DataFrame(sql_query_result).to_markdown(index=False, floatfmt=".3f")

    def uuid_json_encoder(obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex

    sql_query_result_table_source = pd.DataFrame(sql_query_result) \
        .to_json(orient="table", force_ascii=False, index=False, default_handler=uuid_json_encoder)

    return DatabasePredictionRead(
        answer=sql_description,
        sql=f"~~~sql\n{sql_query}\n~~~",
        table=sql_query_result_markdown,
        table_source=sql_query_result_table_source,
        similar_queries=similar_queries
    )
