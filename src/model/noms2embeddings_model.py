from pandas import DataFrame, read_sql
from rq import get_current_job

from infra.chroma_store import connect_to_chroma_collection, create_embeddings_by_chunks
from infra.redis_queue import get_redis_queue, QueueName, MAX_JOB_TIMEOUT, get_job
from scheme.nomenclature_scheme import JobIdRead, CreateAndSaveEmbeddingsResult
from util.features_extraction import extract_features, FEATURES_REGEX_PATTERNS


def _fetch_all_noms(db_con_str: str, table_name: str) -> DataFrame:
    st = f"""
        SELECT * 
        FROM {table_name}
        WHERE is_group = FALSE
     """

    return read_sql(st, db_con_str)


def _get_noms_metadatas_with_features(df_noms_with_features: DataFrame) -> list[dict]:
    metadatas = []

    for _, row in df_noms_with_features.iterrows():
        # Извлечение значений регулярных выражений
        regex_values = row[FEATURES_REGEX_PATTERNS.keys()].to_dict()

        # Преобразование ряда в словарь
        metadata = {"group": row['group']}

        # Объединение словарей
        metadata.update(regex_values)
        metadatas.append(metadata)

    return metadatas


def _create_and_save_embeddings(
    db_con_str: str,
    table_name: str,
    collection_name: str,
    chunk_size: int | None,
):
    job = get_current_job()

    df_noms = _fetch_all_noms(
        db_con_str=db_con_str,
        table_name=table_name,
    )
    print(f"Number of nomenclatures: {len(df_noms)}")

    job.meta['total_count'] = len(df_noms)
    job.meta['ready_count'] = 0
    job.save_meta()

    # Извлечение характеристик и добавление их в метаданные
    df_noms_with_features = extract_features(df_noms)
    print(f"Nomenclatures with features:")
    print(df_noms_with_features)

    # Разделяем сложную строку на несколько шагов
    metadatas = _get_noms_metadatas_with_features(df_noms_with_features)

    ids = df_noms_with_features['id'].to_list()
    documents = df_noms_with_features['name'].to_list()

    collection = connect_to_chroma_collection(collection_name)
    create_embeddings_by_chunks(
        collection=collection,
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        chunk_size=chunk_size,
        is_in_job=True
    )


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
    job_meta = job.get_meta(refresh=True)
    job_status = job.get_status(refresh=True)

    result = CreateAndSaveEmbeddingsResult(
        job_id=job_id,
        status=job_status,
        ready_count=job_meta.get("ready_count", None),
        total_count=job_meta.get("total_count", None)
    )

    return result
