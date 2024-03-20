from pandas import DataFrame, read_sql

from infra.chroma_store import delete_embeddings


def fetch_deleted_embeddings(nom_db_con_str: str, table_name: str, sync_period: int) -> DataFrame:
    # TODO: fix request from scheme on google drive
    st = f"""
        SELECT *
        FROM {table_name}
        WHERE deleted_at IS NOT NULL
        ORDER BY deleted_at;
    """

    return read_sql(st, nom_db_con_str)


def synchronize_embeddings(
    nom_db_con_str: str,
    table_name: str,
    chroma_collection_name: str,
    sync_period: int
):
    deleted_embeddings = fetch_deleted_embeddings(
        nom_db_con_str=nom_db_con_str,
        table_name=table_name,
        sync_period=sync_period
    )

    if not deleted_embeddings.empty:
        delete_embeddings()

    pass
