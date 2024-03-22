from datetime import datetime, timedelta

from pandas import DataFrame, read_sql

from infra.chroma_store import is_in_vectorstore, \
    connect_to_chroma_collection, update_collection_with_patch
from scheme.nomenclature_scheme import SyncNomenclaturesPatch, SyncOneNomenclatureCreateOrUpdate, \
    SyncOneNomenclatureDelete


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
    nomenclatures = nomenclatures.to_dict("records")

    for nom in nomenclatures:
        nom["root_group_name"] = get_root_group_name(nom_db_con_str, table_name, nom["Родитель"])

    collection = connect_to_chroma_collection(chroma_collection_name)
    for nom in nomenclatures:
        nom["is_in_vectorstore"] = is_in_vectorstore(collection=collection, ids=nom["Ссылка"])

    chroma_patch = get_chroma_patch_for_sync(nomenclatures)
    update_collection_with_patch(collection, chroma_patch)


def get_chroma_patch_for_sync(nomenclatures: list[dict]) -> list[SyncNomenclaturesPatch]:
    patch_for_chroma: list[SyncNomenclaturesPatch] = []
    for nom in nomenclatures:
        guid = nom['Ссылка']
        parent = nom['Родитель']
        name = nom['Наименование']
        is_deleted = nom["ПометкаУдаления"] == 1
        root_group_name = nom["root_group_name"]

        if not nom["is_in_vectorstore"]:
            if root_group_name == "0001 Новая структура справочника" and not is_deleted:
                patch_for_chroma.append(
                    SyncNomenclaturesPatch(
                        nomenclature_data=SyncOneNomenclatureCreateOrUpdate(
                            id=guid,
                            nomenclature_name=name,
                            group=parent
                        ),
                        action="create"
                    )
                )
            continue

        if root_group_name != "0001 Новая структура справочника" or is_deleted == 1:
            patch_for_chroma.append(
                SyncNomenclaturesPatch(
                    nomenclature_data=SyncOneNomenclatureDelete(
                        id=guid
                    ),
                    action="delete"
                )
            )
            continue

        patch_for_chroma.append(
            SyncNomenclaturesPatch(
                nomenclature_data=SyncOneNomenclatureCreateOrUpdate(
                    id=guid,
                    nomenclature_name=name,
                    group=parent
                ),
                action="update"
            )
        )
        return patch_for_chroma
