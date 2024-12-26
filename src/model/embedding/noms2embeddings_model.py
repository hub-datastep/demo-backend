from pandas import DataFrame, read_sql
from rq import get_current_job

from infra.chroma_store import connect_to_chroma_collection, create_embeddings_by_chunks
from infra.redis_queue import get_redis_queue, QueueName, MAX_JOB_TIMEOUT, get_job
from model.ner.ner import ner_service
from scheme.embedding.embedding_scheme import CreateAndSaveEmbeddingsResult
from scheme.task.task_scheme import JobIdRead
from util.features_extraction import extract_features, get_noms_metadatas_with_features

NOMENCLATURE_COLUMNS_FOR_COLLECTION = [
    "id",
    "material_code",
    "name",
    "group_code",
    "group",
    "internal_group",
    "view_code",
    "view",
]
NOMENCLATURE_COLUMNS_AS_STRING = ", ".join(f'"{col}"' for col in NOMENCLATURE_COLUMNS_FOR_COLLECTION)


def _fetch_all_noms(db_con_str: str, table_name: str) -> DataFrame:
    st = f"""
        SELECT {NOMENCLATURE_COLUMNS_AS_STRING}
        FROM {table_name}
        WHERE "is_group" = FALSE
        AND "is_deleted" = FALSE
     """
    print(st)

    return read_sql(st, db_con_str)


def _create_and_save_embeddings(
    db_con_str: str,
    table_name: str,
    collection_name: str,
    chunk_size: int | None,
):
    job = get_current_job()

    job.meta['general_status'] = "Fetching nomenclatures"
    job.save_meta()

    df_noms = _fetch_all_noms(
        db_con_str=db_con_str,
        table_name=table_name,
    )

    noms_count = len(df_noms)
    print(f"Number of nomenclatures: {noms_count}")

    job.meta['total_count'] = noms_count
    job.meta['ready_count'] = 0

    job.meta['general_status'] = "Extracting features"
    job.save_meta()

    # Извлечение характеристик и добавление их в метаданные
    df_noms_with_features = extract_features(df_noms)
    print(f"Nomenclatures with features:")
    print(df_noms_with_features)

    job.meta['general_status'] = "Extracting brands"
    job.save_meta()

    noms_names_list = df_noms_with_features['name'].to_list()
    df_noms_with_features['brand'] = ner_service.predict(noms_names_list)

    job.meta['general_status'] = "Building metadatas"
    job.save_meta()

    # Получаем метаданные всех номенклатур с характеристиками
    metadatas = get_noms_metadatas_with_features(df_noms_with_features)
    for i, metadata in enumerate(metadatas):
        nom = df_noms_with_features.loc[i]
        # Add additional columns, that not features
        metadatas[i].update({
            "internal_group": str(nom['internal_group']),
            "group": str(nom['group']),
            "view": str(nom['view']),
            "brand": str(nom['brand']),
        })

    ids = df_noms_with_features['id'].to_list()
    documents = df_noms_with_features['name'].to_list()

    job.meta['general_status'] = "Saving to vectorstore"
    job.save_meta()

    collection = connect_to_chroma_collection(collection_name)
    create_embeddings_by_chunks(
        collection=collection,
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        chunk_size=chunk_size,
        is_in_job=True,
    )

    job.meta['general_status'] = "Done"
    job.save_meta()


def start_creating_and_saving_nomenclatures(
    db_con_str: str,
    table_name: str,
    collection_name: str,
    chunk_size: int | None,
):
    queue = get_redis_queue(name=QueueName.SYNCING)
    job = queue.enqueue(
        _create_and_save_embeddings,
        db_con_str,
        table_name,
        collection_name,
        chunk_size,
        result_ttl=-1,
        job_timeout=MAX_JOB_TIMEOUT,
    )
    return JobIdRead(job_id=job.id)


def get_creating_and_saving_nomenclatures_job_result(job_id: str):
    job = get_job(job_id)
    job_status = job.get_status(refresh=True)
    job_meta = job.get_meta(refresh=True)

    result = CreateAndSaveEmbeddingsResult(
        job_id=job_id,
        status=job_status,
        general_status=job_meta.get("general_status", None),
        ready_count=job_meta.get("ready_count", None),
        total_count=job_meta.get("total_count", None)
    )

    return result
