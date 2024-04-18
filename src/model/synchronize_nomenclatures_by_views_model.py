from pandas import read_sql, DataFrame
from rq import get_current_job
from sqlalchemy import text
from tqdm import tqdm

from infra.chroma_store import is_in_vectorstore, \
    connect_to_chroma_collection, update_collection_with_patch
from infra.redis_queue import get_redis_queue, MAX_JOB_TIMEOUT, get_job, QueueName
from scheme.nomenclature_scheme import SyncNomenclaturesChromaPatch, JobIdRead, \
    SyncOneNomenclatureDataRead, SyncNomenclaturesResultRead


def fetch_nomenclatures(db_con_str: str, table_name: str) -> DataFrame:
    st = text(f"""
        SELECT *
        FROM {table_name}
        WHERE ЭтоГруппа = 0
    """)

    return read_sql(st, db_con_str)


# def get_root_group_name(session: Session, nom_id: str, parent: str):
#     current_parent = parent
#     current_nom_id = nom_id
#     root_group: NomenclatureByView
#     while current_parent != "00000000-0000-0000-0000-000000000000":
#         st = select(NomenclatureByView) \
#             .where(NomenclatureByView.id == current_parent)
#         root_group = session.exec(st).first()
#         if root_group is None:
#             raise ParentNotFoundException(
#                 f"Cannot found parent with id={current_parent} for nom with id={current_nom_id}"
#             )
#         current_parent = root_group.group
#         current_nom_id = root_group.id
#
#     root_group_name = root_group.nomenclature_name
#     return root_group_name


def get_chroma_patch_for_sync(
    nomenclatures: DataFrame
) -> list[SyncNomenclaturesChromaPatch]:
    patch_for_chroma: list[SyncNomenclaturesChromaPatch] = []

    for i, nom in tqdm(nomenclatures.iterrows()):
        sync_nom = SyncOneNomenclatureDataRead(
            id=nom['Ссылка'],
            nomenclature_name=nom['Наименование'],
            group=nom['Родитель']
        )

        if not nom['is_in_vectorstore']:
            if not bool.from_bytes(nom['ПометкаУдаления']):
                patch_for_chroma.append(
                    SyncNomenclaturesChromaPatch(
                        nomenclature_data=sync_nom,
                        action="create"
                    )
                )
            continue

        if bool.from_bytes(nom['ПометкаУдаления']):
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
    db_con_str: str,
    table_name: str,
    chroma_collection_name: str,
):
    job = get_current_job()

    print("Getting noms for sync...")
    nomenclatures = fetch_nomenclatures(db_con_str, table_name)
    print(nomenclatures)

    # print("Getting root group for each nom...")
    # for nom in tqdm(nomenclatures):
    #     nom.root_group_name = get_root_group_name(session, nom.id, nom.group)

    collection = connect_to_chroma_collection(chroma_collection_name)
    print("Checking each nom in vectorstore...")
    for i, nom in tqdm(nomenclatures.iterrows()):
        nom['is_in_vectorstore'] = is_in_vectorstore(collection=collection, ids=nom['Ссылка'])

    print("Creating chroma patch for sync...")
    chroma_patch = get_chroma_patch_for_sync(nomenclatures)
    print(f"Chroma patch length: {len(chroma_patch)}")

    job.meta["total_count"] = len(chroma_patch)
    job.meta["ready_count"] = 0
    job.save_meta()

    print("Syncing chroma collection with patch...")
    return update_collection_with_patch(collection, chroma_patch, job)


def start_synchronizing_nomenclatures(
    db_con_str: str,
    table_name: str,
    chroma_collection_name: str,
):
    queue = get_redis_queue(name=QueueName.SYNCING)
    job = queue.enqueue(
        synchronize_nomenclatures,
        db_con_str,
        table_name,
        chroma_collection_name,
        result_ttl=-1,
        job_timeout=MAX_JOB_TIMEOUT,
    )
    return JobIdRead(job_id=job.id)


def get_sync_nomenclatures_job_result(job_id: str):
    job = get_job(job_id)
    job_meta = job.get_meta(refresh=True)
    result = SyncNomenclaturesResultRead(
        job_id=job_id,
        status=job.get_status(refresh=True),
        ready_count=job_meta.get("ready_count", None),
        total_count=job_meta.get("total_count", None)
    )

    job_result = job.return_value(refresh=True)
    if job_result is not None:
        result.updated_nomenclatures = job_result

    return result
