from langchain.utilities import SQLDatabase

databases_connection_pool = dict()


class DatastepSqlDatabase:
    def __init__(
        self,
        database_connection_string: str,
        include_tables: list[str]
    ):
        # TODO: Использовать пулинг из Алхимии
        if not databases_connection_pool.get("foo", None):
            databases_connection_pool["foo"] = SQLDatabase.from_uri(
                database_connection_string,
                include_tables=include_tables
            )

        self.database = databases_connection_pool["foo"]

    def run(self, sql_query):
        return self.database._execute(sql_query)
