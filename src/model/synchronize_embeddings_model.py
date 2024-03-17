from pandas import DataFrame, read_sql

from infra.chroma_store import delete_embeddings


def fetch_deleted_embeddings(nom_db_con_str: str) -> DataFrame:
    st = """
        SELECT *
        FROM nomenclature
        WHERE deleted_at IS NOT NULL
        ORDER BY deleted_at;
    """

    return read_sql(st, nom_db_con_str)


def synchronize_embeddings(
    nom_db_con_str: str
):
    deleted_embeddings = fetch_deleted_embeddings(nom_db_con_str)

    if not deleted_embeddings.empty:
        delete_embeddings()

    pass
