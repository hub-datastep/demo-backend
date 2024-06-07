from pathlib import Path

import joblib
import numpy as np
from chromadb import QueryResult
from chromadb.api.models.Collection import Collection
from fastembed.embedding import FlagEmbedding
from pandas import read_sql, DataFrame
from redis import Redis
from rq import get_current_job
from rq.job import Job, JobStatus
from scheme.classifier_config_scheme import ClassifierConfig
from sqlalchemy import text
from tqdm import tqdm

from infra.chroma_store import connect_to_chroma_collection
from infra.env import REDIS_HOST, REDIS_PASSWORD, DATA_FOLDER_PATH
from infra.redis_queue import get_redis_queue, MAX_JOB_TIMEOUT, QueueName
from scheme.nomenclature_scheme import MappingOneNomenclatureUpload, \
    MappingNomenclaturesResultRead, JobIdRead, MappingOneTargetRead, MappingOneNomenclatureRead
from util.extract_keyword import extract_keyword
from util.features_extraction import extract_features, get_noms_metadatas_with_features
from util.normalize_name import normalize_name

tqdm.pandas()
# noinspection PyTypeChecker
np.set_printoptions(threshold=np.inf)

SIMILAR_NOMS_COUNT = 3


def _get_group_name_by_id(db_con_str: str, table_name: str, group_id: str):
    st = text(f"""
        SELECT "name"
        FROM {table_name}
        WHERE "is_group" = TRUE
        AND "id" = '{group_id}'
    """)
    result = read_sql(st, db_con_str)
    group_name = result['name'].to_list()[0]

    return group_name


def get_nomenclatures_groups(noms: DataFrame, model_id: str) -> list[int]:
    model_path = f"{DATA_FOLDER_PATH}/linear_svc_model_{model_id}.pkl"
    vectorizer_path = f"{DATA_FOLDER_PATH}/vectorizer_{model_id}.pkl"

    if not Path(model_path).exists() or not Path(vectorizer_path).exists():
        raise Exception(f"Model with ID {model_id} not found locally.")

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    return model.predict(vectorizer.transform(noms['normalized']))


def map_on_nom(
    collection: Collection,
    nom_embeddings: np.ndarray,
    group: int,
    most_similar_count: int,
    metadatas_list: list[dict],
    is_hard_params: bool,
) -> list[MappingOneTargetRead] | None:
    # Just sure that group is int
    group = int(group)
    if is_hard_params:
        where_metadatas = {"$and": [{"group": group}, {"$and": metadatas_list}]}
    else:
        where_metadatas = {"$and": [{"group": group}, {"$or": metadatas_list}]}

    nom_embeddings = nom_embeddings.tolist()
    response: QueryResult = collection.query(
        query_embeddings=[nom_embeddings],
        where=where_metadatas,
        n_results=most_similar_count,
    )

    response_ids = response['ids'][0]
    response_documents = response['documents'][0]
    response_distances = response['distances'][0]

    if len(response_ids) == 0:
        return None

    mapped_noms = []
    for i in range(len(response_ids)):
        mapped_noms.append(MappingOneTargetRead(
            nomenclature_guid=response_ids[i],
            nomenclature=response_documents[i],
            similarity_score=response_distances[i],
            nomenclature_params=metadatas_list,
        ))

    return mapped_noms


def convert_nomenclatures_to_df(nomenclatures: list[MappingOneNomenclatureUpload]) -> DataFrame:
    nomenclatures_as_json = [nom.dict().values() for nom in nomenclatures]
    return DataFrame(nomenclatures_as_json, columns=['row_number', 'nomenclature'])


def get_nomenclatures_embeddings(strings: list[str]) -> list[np.ndarray]:
    embedding_model = FlagEmbedding(
        model_name="intfloat/multilingual-e5-large"
    )
    strings = [f"query: {s}" for s in strings]
    result = list(embedding_model.embed(strings))
    return result


def split_nomenclatures_by_chunks(
    nomenclatures: list[MappingOneNomenclatureUpload],
    chunk_size: int = 100,
) -> list[list[MappingOneNomenclatureUpload]]:
    # https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks
    for i in range(0, len(nomenclatures), chunk_size):
        yield nomenclatures[i:i + chunk_size]


def create_mapping_job(
    nomenclatures: list[MappingOneNomenclatureUpload],
    previous_job_id: str | None,
    most_similar_count: int,
    chroma_collection_name: str,
    model_id: str,
    db_con_str: str,
    table_name: str,
    classifier_config: ClassifierConfig,
) -> JobIdRead:
    queue = get_redis_queue(name=QueueName.MAPPING)
    job = queue.enqueue(
        map_nomenclatures_chunk,
        nomenclatures,
        most_similar_count,
        chroma_collection_name,
        model_id,
        db_con_str,
        table_name,
        meta={
            "previous_nomenclature_id": previous_job_id
        },
        result_ttl=-1,
        job_timeout=MAX_JOB_TIMEOUT,
        classifier_config=classifier_config,
    )
    return JobIdRead(job_id=job.id)


def start_mapping(
    nomenclatures: list[MappingOneNomenclatureUpload],
    most_similar_count: int,
    chroma_collection_name: str,
    chunk_size: int,
    model_id: str,
    db_con_str: str,
    table_name: str,
    classifier_config: ClassifierConfig
) -> JobIdRead:
    segments = split_nomenclatures_by_chunks(
        nomenclatures=nomenclatures,
        chunk_size=chunk_size,
    )
    last_job_id = None
    for segment in segments:
        job = create_mapping_job(
            nomenclatures=segment,
            previous_job_id=last_job_id,
            most_similar_count=most_similar_count,
            chroma_collection_name=chroma_collection_name,
            model_id=model_id,
            db_con_str=db_con_str,
            table_name=table_name,
            classifier_config=classifier_config,
        )
        last_job_id = job.job_id

    return JobIdRead(job_id=last_job_id)


def map_nomenclatures_chunk(
    nomenclatures: list[MappingOneNomenclatureUpload],
    most_similar_count: int,
    chroma_collection_name: str,
    model_id: str,
    db_con_str: str,
    table_name: str,
    classifier_config: ClassifierConfig
) -> list[MappingOneNomenclatureRead]:
    job = get_current_job()

    # Convert nomenclatures to DataFrame
    noms = convert_nomenclatures_to_df(nomenclatures)

    job.meta['total_count'] = len(noms)
    job.meta['ready_count'] = 0
    job.save_meta()

    # Normalize nomenclatures names
    noms['normalized'] = noms['nomenclature'].progress_apply(
        lambda nom_name: normalize_name(nom_name)
    )

    # Classification to get nomenclature group
    noms['group'] = get_nomenclatures_groups(noms, model_id)

    # Get group name of every nomenclature
    noms['group_name'] = noms['group'].progress_apply(
        lambda group_id: _get_group_name_by_id(
            db_con_str=db_con_str,
            table_name=table_name,
            group_id=group_id,
        )
    )
    if classifier_config.is_use_keywords_detection:
        noms['keyword'] = noms['normalized'].progress_apply(
            lambda nom_name: extract_keyword(nom_name)
        )
    else:
        noms['keyword'] = None

    # Create embeddings for every nomenclature
    noms['embeddings'] = get_nomenclatures_embeddings(noms['nomenclature'].to_list())

    # Copy noms to name column for extracting features
    noms['name'] = noms['nomenclature']
    # Извлечение характеристик и добавление их в метаданные
    noms = extract_features(noms)

    # Получаем метаданные всех номенклатур с характеристиками
    noms['metadata'] = get_noms_metadatas_with_features(noms)

    collection = connect_to_chroma_collection(collection_name=chroma_collection_name)

    noms['mappings'] = None
    noms['similar_mappings'] = None
    for i, nom in tqdm(noms.iterrows()):
        metadatas_list = []
        for key, val in nom['metadata'].items():
            metadatas_list.append({str(key): val})

        is_use_keywords = classifier_config.is_use_keywords_detection

        # Check if nom really belong to mapped group, only if is_use_keywords is True
        if is_use_keywords and nom['keyword'] not in nom['group_name'].lower():
            nom['mappings'] = [MappingOneTargetRead(
                nomenclature_guid="",
                nomenclature="Для такой номенклатуры группы не нашлось",
                similarity_score=-1,
                nomenclature_params=metadatas_list,
            )]
        else:
            # Map nomenclature with equal group and params
            mappings = map_on_nom(
                collection=collection,
                nom_embeddings=nom['embeddings'],
                group=nom['group'],
                most_similar_count=most_similar_count,
                metadatas_list=metadatas_list,
                is_hard_params=True,
            )
            nom['mappings'] = mappings

            # Map similar nomenclatures if nom's params is not valid
            if mappings is None:
                similar_mappings = map_on_nom(
                    collection=collection,
                    nom_embeddings=nom['embeddings'],
                    group=nom['group'],
                    most_similar_count=SIMILAR_NOMS_COUNT,
                    metadatas_list=metadatas_list,
                    is_hard_params=False,
                )
                nom['similar_mappings'] = similar_mappings
        noms.loc[i] = nom
        job.meta['ready_count'] += 1
        job.save_meta()

    job.meta['status'] = "finished"
    job.save_meta()

    noms['embeddings'] = None

    noms_dict = noms.to_dict(orient="records")
    result_nomenclatures = [MappingOneNomenclatureRead(**nom) for nom in noms_dict]

    return result_nomenclatures

def get_jobs_from_rq(nomenclature_id: str) -> list[MappingNomenclaturesResultRead]:
    redis = Redis(host=REDIS_HOST, password=REDIS_PASSWORD)
    jobs_list: list[MappingNomenclaturesResultRead] = []

    prev_job_id = nomenclature_id
    while prev_job_id is not None:
        job = Job.fetch(prev_job_id, connection=redis)
        job_meta = job.get_meta(refresh=True)
        job_status = job.get_status(refresh=True)
        job_result = MappingNomenclaturesResultRead(
            job_id=job.id,
            ready_count=job_meta.get("ready_count", None),
            total_count=job_meta.get("total_count", None),
            general_status=job_status,
        )

        if job_status == JobStatus.FINISHED:
            result_mappings: list[MappingOneNomenclatureRead] = job.return_value(refresh=True)
            job_result.nomenclatures = result_mappings

        jobs_list.append(job_result)
        prev_job_id = job_meta['previous_nomenclature_id']

    return jobs_list


def get_all_jobs(nomenclature_id: str) -> list[MappingNomenclaturesResultRead]:
    jobs_from_rq = get_jobs_from_rq(nomenclature_id)
    return jobs_from_rq
