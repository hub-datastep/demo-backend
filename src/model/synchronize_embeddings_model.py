from datetime import datetime, timedelta

from pandas import DataFrame, read_sql

from infra.chroma_store import delete_embeddings, add_embeddings, update_embeddings, is_in_vectorstore, \
    connect_to_chroma_collection


def fetch_nomenclatures(nom_db_con_str: str, table_name: str, sync_period: int) -> DataFrame:
    sync_date = datetime.now() - timedelta(hours=sync_period)

    st = f"""
        SELECT *
        FROM {table_name}
        WHERE "ЭтоГруппа" = 0 
        AND "МСУ_ДатаИзменения" BETWEEN '{sync_date}' AND '{datetime.now()}';
    """

    return read_sql(st, nom_db_con_str)


def get_root_group_name(nom_db_con_str: str, table_name: str, parent):
    current_parent = parent
    root_group = DataFrame()
    while current_parent != "00000000-0000-0000-0000-000000000000":
        st = f"""
            SELECT *
            FROM {table_name}
            WHERE "Ссылка" = '{current_parent}'
        """
        root_group = read_sql(st, nom_db_con_str)
        current_parent = str(root_group['Родитель'].item())

    root_group_name = root_group['Наименование'].item()
    return root_group_name


def synchronize_embeddings(
    nom_db_con_str: str,
    table_name: str,
    chroma_collection_name: str,
    sync_period: int
):
    nomenclatures = fetch_nomenclatures(nom_db_con_str, table_name, sync_period)
    collection = connect_to_chroma_collection(chroma_collection_name)
    for _, row in nomenclatures.iterrows():
        guid = str(row['Ссылка'])
        parent = str(row['Родитель'])
        name = str(row['Наименование'])
        metadatas = {"group": parent}
        root_group_name = get_root_group_name(nom_db_con_str, table_name, parent)

        if not is_in_vectorstore(collection=collection, ids=guid):
            if root_group_name == "0001 Новая структура справочника" and row['ПометкаУдаления'] == 0:
                add_embeddings(
                    collection=collection,
                    ids=guid,
                    documents=name,
                    metadatas=metadatas,
                )
                print(f"Добавлен: {guid}")
            continue

        if root_group_name != "0001 Новая структура справочника" or row['ПометкаУдаления'] == 1:
            delete_embeddings(
                collection=collection,
                ids=guid,
            )
            print(f"Удалён: {guid}")
            continue

        update_embeddings(
            collection=collection,
            ids=guid,
            documents=name,
            metadatas=metadatas
        )
        print(f"Обновлён: {guid}")
