import ast
import json
from pathlib import Path

import joblib
import numpy as np
from chromadb import QueryResult
from fastapi import HTTPException
from fastembed.embedding import FlagEmbedding
from pandas import read_sql, DataFrame
from redis import Redis
from rq import get_current_job
from rq.job import Job, JobStatus
from sqlalchemy import text
from tqdm import tqdm

from infra.chroma_store import connect_to_chroma_collection
from infra.env import REDIS_HOST, REDIS_PASSWORD, DB_CONNECTION_STRING, DATA_FOLDER_PATH
from infra.redis_queue import get_redis_queue, MAX_JOB_TIMEOUT, QueueName
from scheme.nomenclature_scheme import MappingOneNomenclatureRead, \
    MappingOneNomenclatureUpload, \
    MappingNomenclaturesResultRead, JobIdRead
from util.extract_keyword import extract_keyword
from util.features_extraction import extract_features, get_noms_metadatas_with_features
from util.normalize_name import normalize_name

tqdm.pandas()
# noinspection PyTypeChecker
np.set_printoptions(threshold=np.inf)


def _get_group_name_by_id(db_con_str: str, table_name: str, group_id: str):
    st = text(f"""
        SELECT "name"
        FROM {table_name}
        WHERE "is_group" = TRUE
        AND "id" = '{group_id}'
    """)
    result = read_sql(st, db_con_str)
    group_name = result['name'].to_list()[0].lower()

    return group_name


def get_nomenclatures_groups(noms: DataFrame, model_id: str) -> list[str]:
    model_path = f"{DATA_FOLDER_PATH}/linear_svc_model_{model_id}.pkl"
    vectorizer_path = f"{DATA_FOLDER_PATH}/vectorizer_{model_id}.pkl"

    if not Path(model_path).exists() or not Path(vectorizer_path).exists():
        raise HTTPException(
            status_code=400,
            detail=f"Model with ID {model_id} not found locally.",
        )

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    return model.predict(vectorizer.transform(noms['normalized']))


def map_on_nom(
    nom_embeddings: np.ndarray,
    group: str,
    most_similar_count: int,
    chroma_collection_name: str,
    metadata: dict,
    # ) -> list[MappingOneTargetRead]:
) -> list[dict]:
    collection = connect_to_chroma_collection(collection_name=chroma_collection_name)

    metadatas_list = []
    for key, val in metadata.items():
        metadatas_list.append({key: val})

    nom_embeddings = nom_embeddings.tolist()
    response: QueryResult = collection.query(
        query_embeddings=[nom_embeddings],
        n_results=most_similar_count,
        where={"$and": metadatas_list},
    )

    # TODO: сделать поиск без параметров, чтобы выдавать аналоги

    # found_noms_count = len(response['ids'][0])
    # if found_noms_count == 0:
    #     raise NomsInChromaNotFoundException(
    #         f"В коллекции Chroma {chroma_collection_name} нет номенклатур, принадлежащих группе {group}."
    #     )

    mapped_noms = []
    for i in range(len(response['ids'][0])):
        # mapped_noms.append(MappingOneTargetRead(
        #     nomenclature_guid=response['ids'][0][i],
        #     nomenclature=response['documents'][0][i],
        #     similarity_score=response['distances'][0][i],
        # ))
        mapped_noms.append({
            "nomenclature_guid": response['ids'][0][i],
            "nomenclature": response['documents'][0][i],
            "similarity_score": response['distances'][0][i],
        })

    return mapped_noms


def convert_nomenclatures_to_df(nomenclatures: list[MappingOneNomenclatureUpload]) -> DataFrame:
    nomenclatures_as_json = [nom.dict().values() for nom in nomenclatures]
    return DataFrame(nomenclatures_as_json, columns=['row_number', 'nomenclature'])


def get_nom_candidates(groups: list[str]) -> DataFrame:
    groups_str = ", ".join([f"'{g}'" for g in groups])
    candidates = read_sql(
        f'SELECT * FROM nomenclature WHERE "group" in ({groups_str})',
        DB_CONNECTION_STRING
    )
    candidates = candidates.replace({np.nan: "[]"})
    candidates.embeddings = candidates.embeddings.progress_apply(ast.literal_eval).progress_apply(np.array)
    return candidates


def get_nomenclatures_embeddings(strings: list[str]) -> list[np.ndarray]:
    embedding_model = FlagEmbedding(
        model_name="intfloat/multilingual-e5-large"
    )
    strings = [f"query: {s}" for s in strings]
    result = list(embedding_model.embed(strings))
    return result


def split_nomenclatures_by_chunks(
    nomenclatures: list[MappingOneNomenclatureUpload],
    chunk_size: int = 100
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
        job_timeout=MAX_JOB_TIMEOUT
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
):
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
    print(noms['group_name'].to_list())

    noms['keyword'] = noms['normalized'].progress_apply(
        lambda nom_name: extract_keyword(nom_name)
    )

    # Create embeddings for every nomenclature
    noms['embeddings'] = get_nomenclatures_embeddings(noms['nomenclature'].to_list())

    # Copy noms to name column for extracting features
    noms['name'] = noms['nomenclature']
    # Извлечение характеристик и добавление их в метаданные
    noms = extract_features(noms)

    # Получаем метаданные всех номенклатур с характеристиками
    noms['metadata'] = get_noms_metadatas_with_features(noms)

    noms['mappings'] = None
    for i, nom in tqdm(noms.iterrows()):
        # try:

        # Check if nom really belong to mapped group
        if nom['keyword'] not in nom['group_name']:
            # nom['mappings'] = [MappingOneTargetRead(
            #     nomenclature_guid="",
            #     nomenclature="Нет группы для такой номенклатуры",
            #     similarity_score=0,
            # )]
            nom['mappings'] = [{
                "nomenclature_guid": "",
                "nomenclature": "Для такой номенклатуры группы не нашлось",
                "similarity_score": 0,
            }]
        else:
            nom['mappings'] = map_on_nom(
                nom_embeddings=nom['embeddings'],
                group=nom['group'],
                most_similar_count=most_similar_count,
                chroma_collection_name=chroma_collection_name,
                metadata=nom['metadata'],
            )

        # except NomsInChromaNotFoundException:
        #     pass

        noms.loc[i] = nom
        job.meta['ready_count'] += 1
        job.save_meta()

    job.meta['status'] = "finished"
    job.save_meta()

    return noms.to_json(orient="records", force_ascii=False)


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
            nomenclatures=[]
        )

        if job_status == JobStatus.FINISHED:
            result_json = job.return_value()
            result_dict = json.loads(result_json)
            job_result.nomenclatures = [MappingOneNomenclatureRead(**d) for d in result_dict]

        jobs_list.append(job_result)
        prev_job_id = job_meta['previous_nomenclature_id']

    return jobs_list


def get_all_jobs(nomenclature_id: str) -> list[MappingNomenclaturesResultRead]:
    jobs_from_rq = get_jobs_from_rq(nomenclature_id)
    return jobs_from_rq
