from datetime import datetime, timedelta

from pandas import DataFrame, read_sql

from infra.chroma_store import delete_embeddings, add_embeddings, update_embeddings, is_in_vectorstore, connect_to_chroma_collection


def fetch_nomenclatures(nom_db_con_str: str, table_name: str, sync_period: int) -> DataFrame:
    sync_date = datetime.now() - timedelta(hours=sync_period)

    st = f"""
        SELECT *
        FROM {table_name}
        WHERE "ЭтоГруппа" = 0 
        AND "МСУ_ДатаИзменения" BETWEEN '{sync_date}' AND '{datetime.now()}';
    """

    return read_sql(st, nom_db_con_str)


def get_root_group(nom_db_con_str: str, table_name: str, parent) -> DataFrame:
    current_parent = parent
    root_group_name = ""
    while current_parent != 'e29a2c8c-dad2-11ea-8e35-001e67bc1b0d':
        st = f"""
            SELECT *
            FROM {table_name}
            WHERE "Ссылка" = '{current_parent}'
        """
        root_group = read_sql(st, nom_db_con_str)
        root_group_name = root_group['Наименование'].item()
        current_parent = root_group['Родитель'].item()
    return root_group_name


def synchronize_nomenclatures(
    nom_db_con_str: str,
    table_name: str,
    chroma_collection_name: str,
    sync_period: int
):
    nomenclatures = fetch_nomenclatures(nom_db_con_str, table_name, sync_period)
    collection = connect_to_chroma_collection(chroma_collection_name)
    for index, row in nomenclatures.iterrows():
        guid = row['Ссылка']
        parent = row['Родитель']
        name = row['Наименование']
        metadatas = {"group": parent}

        if is_in_vectorstore(guid):
            add_embeddings(
                collection=collection,
                ids=guid,
                documents=name,
                metadatas=metadatas
            )
            print(f"Добавлен: {guid}")
            continue

        if row['ПометкаУдаления'] == 1:
            delete_embeddings(guid)
            print(f"Удалён: {guid}")
            continue

        root_group = get_root_group(nom_db_con_str, table_name, parent)
        if root_group != "0001 Новая структура справочника":
            delete_embeddings(guid)
            print(f"Корневой родитель {guid} не 0001 Новая структура справочника")
            continue

        update_embeddings(
            collection=collection,
            ids=guid,
            documents=name,
            metadatas=metadatas
        )
        print(f"Обновлён: {guid}")

