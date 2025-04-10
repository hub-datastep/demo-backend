DEFAULT_HISTORY_SCHEMA = "public"


def get_db_schema_by_client(client: str | None = None) -> str:
    if client is None:
        return DEFAULT_HISTORY_SCHEMA
    return client
