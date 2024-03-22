from datetime import datetime, timedelta

from sqlalchemy import Engine
from sqlmodel import create_engine, Session, select, between

from infra.chroma_store import is_in_vectorstore, \
    connect_to_chroma_collection, update_collection_with_patch
from scheme.nomenclature_scheme import SyncNomenclaturesPatch, SyncOneNomenclatureCreateOrUpdate, \
    SyncOneNomenclatureDelete, MsuDatabaseOneNomenclatureRead


def fetch_nomenclatures(engine: Engine, sync_period: int) -> list[MsuDatabaseOneNomenclatureRead]:
    with Session(engine) as session:
        st = select(MsuDatabaseOneNomenclatureRead) \
            .where(MsuDatabaseOneNomenclatureRead.is_group == 0) \
            .where(
            between(
                expr=MsuDatabaseOneNomenclatureRead.edited_at,
                lower_bound=datetime.now() - timedelta(hours=sync_period),
                upper_bound=datetime.now()
            ))
        result = session.exec(st).all()

    return list(result)


def get_root_group_name(engine: Engine, parent: str):
    with Session(engine) as session:
        current_parent = parent
        root_group: MsuDatabaseOneNomenclatureRead
        while current_parent != "00000000-0000-0000-0000-000000000000":
            st = select(MsuDatabaseOneNomenclatureRead) \
                .where(MsuDatabaseOneNomenclatureRead.id == current_parent)
            root_group = session.exec(st).first()
            current_parent = str(root_group.group)

    root_group_name = root_group.nomenclature_name
    return root_group_name


def synchronize_nomenclatures(
    nom_db_con_str: str,
    chroma_collection_name: str,
    sync_period: int
):
    engine = create_engine(nom_db_con_str)
    nomenclatures: list[MsuDatabaseOneNomenclatureRead] = fetch_nomenclatures(engine, sync_period)
    for nom in nomenclatures:
        nom.root_group_name = get_root_group_name(engine, str(nom.group))

    collection = connect_to_chroma_collection(chroma_collection_name)
    for nom in nomenclatures:
        nom.is_in_vectorstore = is_in_vectorstore(collection=collection, ids=str(nom.id))

    chroma_patch = get_chroma_patch_for_sync(nomenclatures)
    update_collection_with_patch(collection, chroma_patch)


def get_chroma_patch_for_sync(nomenclatures: list[MsuDatabaseOneNomenclatureRead]) -> list[SyncNomenclaturesPatch]:
    patch_for_chroma: list[SyncNomenclaturesPatch] = []
    for nom in nomenclatures:
        if not nom.is_in_vectorstore:
            if str(nom.root_group_name) == "0001 Новая структура справочника" and not nom.is_deleted:
                patch_for_chroma.append(
                    SyncNomenclaturesPatch(
                        nomenclature_data=SyncOneNomenclatureCreateOrUpdate(
                            id=str(nom.id),
                            nomenclature_name=str(nom.nomenclature_name),
                            group=str(nom.group)
                        ),
                        action="create"
                    )
                )
            continue

        if str(nom.root_group_name) != "0001 Новая структура справочника" or nom.is_deleted:
            patch_for_chroma.append(
                SyncNomenclaturesPatch(
                    nomenclature_data=SyncOneNomenclatureDelete(
                        id=str(nom.id)
                    ),
                    action="delete"
                )
            )
            continue

        patch_for_chroma.append(
            SyncNomenclaturesPatch(
                nomenclature_data=SyncOneNomenclatureCreateOrUpdate(
                    id=str(nom.id),
                    nomenclature_name=str(nom.nomenclature_name),
                    group=str(nom.group)
                ),
                action="update"
            )
        )

    return patch_for_chroma
