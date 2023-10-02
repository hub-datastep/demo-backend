import pandas as pd

from datastep.components.datastep_sql_database import DatastepSqlDatabase
from dto.datastep_prediction_dto import DatastepPredictionDto
from datastep.datastep_chains.datastep_markdown_chain import DatastepMarkdownChain
from datastep.datastep_chains.datastep_sql_chain import DatastepSqlChain
from dto.query_dto import QueryDto


async def datastep_get_prediction(body: QueryDto) -> DatastepPredictionDto:
    # TODO: Брать connection string из файлика
    # TODO: PromptRepository.get_active_prompt(tenant_id); tenant_id брать из аргументов функции

    datastep_sql_database = DatastepSqlDatabase(
        database_connection_string="postgresql://qvzibsah:7wNHUBB3BMnY6QiFi0ggBejNd3SmlRf2@trumpet.db.elephantsql.com/qvzibsah",
        include_tables=body.tables
    )
    datastep_sql_chain = DatastepSqlChain(sql_database=datastep_sql_database.database)
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
