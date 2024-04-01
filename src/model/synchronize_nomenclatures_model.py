from datetime import datetime, timedelta

from sqlalchemy import Engine
from sqlmodel import create_engine, Session, select, between
from tqdm import tqdm

from infra.chroma_store import is_in_vectorstore, \
    connect_to_chroma_collection, update_collection_with_patch
from infra.redis_queue import get_redis_queue, MAX_JOB_TIMEOUT, get_job, QueueName
from scheme.nomenclature_scheme import SyncNomenclaturesChromaPatch, MsuDatabaseOneNomenclatureRead, JobIdRead, \
    SyncOneNomenclatureDataRead, SyncNomenclaturesResultRead


def fetch_nomenclatures(engine: Engine, sync_period: int) -> list[MsuDatabaseOneNomenclatureRead]:
    print("Fetch nomenclatures starts")
    with Session(engine) as session:
        st = select(MsuDatabaseOneNomenclatureRead) \
            .where(MsuDatabaseOneNomenclatureRead.is_group == 0) \
            .where(between(
                expr=MsuDatabaseOneNomenclatureRead.edited_at,
                lower_bound=datetime.now() - timedelta(hours=sync_period),
                upper_bound=datetime.now()
            ))
        result = session.exec(st).all()
        print(f"noms: {result}")

    print("Fetch nomenclatures finished")
    return list(result)


def get_root_group_name(engine: Engine, nom_id: str, parent: str):
    class ParentNotFoundException(Exception):
        pass

    with Session(engine) as session:
        current_parent = parent
        current_nom_id = nom_id
        root_group: MsuDatabaseOneNomenclatureRead
        while current_parent != "00000000-0000-0000-0000-000000000000":
            st = select(MsuDatabaseOneNomenclatureRead) \
                .where(MsuDatabaseOneNomenclatureRead.id == current_parent)
            root_group = session.exec(st).first()
            if root_group is None:
                raise ParentNotFoundException(
                    f"Cannot found parent with id={current_parent} for nom with id={current_nom_id}"
                )
            current_parent = root_group.group
            current_nom_id = root_group.id

    root_group_name = root_group.nomenclature_name
    return root_group_name


def get_chroma_patch_for_sync(
    nomenclatures: list[MsuDatabaseOneNomenclatureRead]
) -> list[SyncNomenclaturesChromaPatch]:
    target_root_name = "Загрузка"
    patch_for_chroma: list[SyncNomenclaturesChromaPatch] = []
    for nom in nomenclatures:
        sync_nom = SyncOneNomenclatureDataRead(
            id=nom.id,
            nomenclature_name=nom.nomenclature_name,
            group=nom.group
        )

        if not nom.is_in_vectorstore:
            if nom.root_group_name == target_root_name and not bool.from_bytes(nom.is_deleted):
                patch_for_chroma.append(
                    SyncNomenclaturesChromaPatch(
                        nomenclature_data=sync_nom,
                        action="create"
                    )
                )
            continue

        if nom.root_group_name != target_root_name or bool.from_bytes(nom.is_deleted):
            patch_for_chroma.append(
                SyncNomenclaturesChromaPatch(
                    nomenclature_data=sync_nom,
                    action="delete"
                )
            )
            continue

        patch_for_chroma.append(
            SyncNomenclaturesChromaPatch(
                nomenclature_data=sync_nom,
                action="update"
            )
        )

    return patch_for_chroma


def synchronize_nomenclatures(
    nom_db_con_str: str,
    chroma_collection_name: str,
    sync_period: int,
):
    print("Create engine starts")
    engine = create_engine(nom_db_con_str)
    nomenclatures: list[MsuDatabaseOneNomenclatureRead] = fetch_nomenclatures(engine, sync_period)
    print(len(nomenclatures))
    for nom in tqdm(nomenclatures):
        nom.root_group_name = get_root_group_name(engine, nom.id, nom.group)

    collection = connect_to_chroma_collection(chroma_collection_name)
    for nom in nomenclatures:
        nom.is_in_vectorstore = is_in_vectorstore(collection=collection, ids=nom.id)

    chroma_patch = get_chroma_patch_for_sync(nomenclatures)
    print(f"chroma patch: {chroma_patch}")
    return update_collection_with_patch(collection, chroma_patch)


def start_synchronizing_nomenclatures(
    nom_db_con_str: str,
    chroma_collection_name: str,
    sync_period: int,
):
    queue = get_redis_queue(name=QueueName.SYNCING)
    job = queue.enqueue(
        synchronize_nomenclatures,
        nom_db_con_str,
        chroma_collection_name,
        sync_period,
        result_ttl=-1,
        job_timeout=MAX_JOB_TIMEOUT,
    )
    return JobIdRead(job_id=job.id)


def get_sync_nomenclatures_job_result(job_id: str):
    job = get_job(job_id)

    result = SyncNomenclaturesResultRead(
        job_id=job_id,
        status=job.get_status(refresh=True)
    )

    job_result = job.return_value(refresh=True)
    if job_result is not None:
        result.updated_nomenclatures = job_result

    return result
