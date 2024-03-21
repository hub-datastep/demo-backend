from pandas import DataFrame, read_sql
from datetime import datetime, timedelta

# from infra.chroma_store import delete_embeddings


def fetch_nomenclatures(nom_db_con_str: str, table_name: str, sync_period: int) -> DataFrame:
    sync_date = datetime.now() - timedelta(hours=sync_period)

    st = f"""
        SELECT *
        FROM {table_name}
        WHERE "ЭтоГруппа" = 0 
        AND "МСУ_ДатаИзменения" BETWEEN '{sync_date}' AND '{datetime.now()}';
    """

    return read_sql(st, nom_db_con_str)

def get_group_root(nom_db_con_str: str, table_name: str, parent) -> DataFrame:
    current_parent = parent
    while current_parent != 'e29a2c8c-dad2-11ea-8e35-001e67bc1b0d':
        st = f"""
            SELECT *
            FROM {table_name}
            WHERE "Ссылка" = '{current_parent}'
        """
        current_parent = read_sql(st, nom_db_con_str)[0]['Родитель']
    return read_sql(st, nom_db_con_str)[0]['Ссылка']



def synchronize_nomenclatures(
    nom_db_con_str: str,
    table_name: str,
    # chroma_collection_name: str,
    sync_period: int
):
    nomenclatures = fetch_nomenclatures(nom_db_con_str, table_name, sync_period)
    for index, row in nomenclatures.iterrows():
        guid = row['Ссылка']
        parent = row['Родитель']
        group_root = get_group_root(nom_db_con_str, table_name, parent)

        # if guid not in vectorstore:
            # add_nomenclature_to_vectorstore(guid)
            # continue

        if row['ПометкаУдаления'] == 1:
            # delete_nomenclature_by_guid(guid)
            print('Удалить')
            continue

        if group_root != "0001 Новая структура справочника":
            # delete_nomenclature_by_guid(guid)
            print("Не справочник")
            continue

        # Update embedding in vectorstore by GUID or group
        # update_embedding_in_vectorstore(guid, group_root)

    return "Synchronization completed successfully"

