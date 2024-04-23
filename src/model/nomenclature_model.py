import ast
import json
import os

import joblib
import numpy as np
from chromadb import HttpClient, QueryResult
from fastembed.embedding import FlagEmbedding
from pandas import read_sql, DataFrame
from redis import Redis
from rq import get_current_job
from rq.job import Job, JobStatus
from tqdm import tqdm

from exception.noms_in_chroma_not_found_exception import NomsInChromaNotFoundException
from infra.redis_queue import get_redis_queue, MAX_JOB_TIMEOUT, QueueName
from model.retrain_classifier_by_views_model import normalize_nom_name
from scheme.nomenclature_scheme import MappingNomenclaturesUpload, MappingOneNomenclatureRead, \
    MappingOneNomenclatureUpload, \
    MappingNomenclaturesResultRead, JobIdRead

tqdm.pandas()
np.set_printoptions(threshold=np.inf)


def map_on_group(noms: DataFrame, model_id: str) -> list:
    model = joblib.load(f"{os.getenv('DATA_FOLDER_PATH')}/linear_svc_model_{model_id}.pkl")
    count_vect = joblib.load(f"{os.getenv('DATA_FOLDER_PATH')}/vectorizer_{model_id}.pkl")
    # return model.predict(count_vect.transform(noms["nomenclature"]))
    return model.predict(count_vect.transform(noms['normalized']))


def map_on_nom(nom_embeddings: np.ndarray, group: str, most_similar_count: int, chroma_collection_name: str):
    chroma = HttpClient(host=os.getenv("CHROMA_HOST"), port=os.getenv("CHROMA_PORT"))
    collection = chroma.get_collection(name=chroma_collection_name)

    nom_embeddings = nom_embeddings.tolist()
    response: QueryResult = collection.query(
        query_embeddings=[nom_embeddings],
        n_results=most_similar_count,
        where={"group": group}
    )

    found_noms_count = len(response["ids"][0])

    if found_noms_count == 0:
        raise NomsInChromaNotFoundException(
            f"В коллекции Chroma {chroma_collection_name} нет номенклатур, принадлежащих группе {group}."
        )

    mapped_noms = []
    for i in range(len(response["ids"][0])):
        mapped_noms.append({
            "nomenclature_guid": response["ids"][0][i],
            "nomenclature": response["documents"][0][i],
            "similarity_score": response["distances"][0][i]
        })

    return mapped_noms


def parse_txt_file(nomenclatures: list[MappingOneNomenclatureUpload]) -> DataFrame:
    nomenclatures_as_json = [nom.dict().values() for nom in nomenclatures]
    return DataFrame(nomenclatures_as_json, columns=["row_number", "nomenclature"])


def get_nom_candidates(groups: list[str]) -> DataFrame:
    groups_str = ", ".join([f"'{g}'" for g in groups])
    candidates = read_sql(
        f'SELECT * FROM nomenclature WHERE "group" in ({groups_str})',
        os.getenv("DB_CONNECTION_STRING")
    )
    candidates = candidates.replace({np.nan: "[]"})
    candidates.embeddings = candidates.embeddings.progress_apply(ast.literal_eval).progress_apply(np.array)
    return candidates


def get_embeddings(strings: list[str]) -> list[np.ndarray]:
    embedding_model = FlagEmbedding(
        model_name="intfloat/multilingual-e5-large"
    )
    strings = [f"query: {s}" for s in strings]
    result = list(embedding_model.embed(strings))
    return result


def nomenclature_segments(
    nomenclatures: list[MappingOneNomenclatureUpload],
    segment_length: int = 100
) -> list[list[MappingOneNomenclatureUpload]]:
    # https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks
    for i in range(0, len(nomenclatures), segment_length):
        yield nomenclatures[i:i + segment_length]


def create_job(
    nomenclatures: list[MappingOneNomenclatureUpload],
    previous_job_id: str | None,
    most_similar_count: int,
    chroma_collection_name: str,
    model_id: str,
) -> JobIdRead:
    queue = get_redis_queue(name=QueueName.MAPPING)
    job = queue.enqueue(
        process,
        nomenclatures,
        most_similar_count,
        chroma_collection_name,
        model_id,
        meta={
            "previous_nomenclature_id": previous_job_id
        },
        result_ttl=-1,
        job_timeout=MAX_JOB_TIMEOUT
    )
    return JobIdRead(job_id=job.id)


def start_mapping(nomenclatures: MappingNomenclaturesUpload, model_id: str) -> JobIdRead:
    nomenclatures_list = nomenclatures.nomenclatures
    most_similar_count = nomenclatures.most_similar_count
    chroma_collection_name = nomenclatures.chroma_collection_name

    last_job_id = None
    for segment in nomenclature_segments(nomenclatures_list, segment_length=nomenclatures.job_size):
        job = create_job(
            nomenclatures=segment,
            previous_job_id=last_job_id,
            most_similar_count=most_similar_count,
            chroma_collection_name=chroma_collection_name,
            model_id=model_id
        )
        last_job_id = job.job_id

    return JobIdRead(job_id=last_job_id)


def process(
    nomenclatures: list[MappingOneNomenclatureUpload],
    most_similar_count: int,
    chroma_collection_name: str,
    model_id: str,
    use_jobs: bool = True
):
    if use_jobs:
        job = get_current_job()

    noms: DataFrame = parse_txt_file(nomenclatures)

    if use_jobs:
        job.meta["total_count"] = len(noms)
        job.meta["ready_count"] = 0
        job.save_meta()

    noms['normalized'] = noms['nomenclature'].progress_apply(
        lambda nom: normalize_nom_name(nom)
    )

    noms['group'] = map_on_group(noms, model_id)
    noms['mappings'] = None

    noms['embeddings'] = get_embeddings(noms.nomenclature.to_list())

    for i, nom in tqdm(noms.iterrows()):
        try:
            nom.mappings = map_on_nom(nom.embeddings, nom.group, most_similar_count, chroma_collection_name)
        except NomsInChromaNotFoundException:
            pass
        noms.loc[i] = nom
        if use_jobs:
            job.meta['ready_count'] += 1
            job.save_meta()

    if use_jobs:
        job.meta['status'] = "finished"
        job.save_meta()

    return noms.to_json(orient="records", force_ascii=False)


def get_jobs_from_rq(nomenclature_id: str) -> list[MappingNomenclaturesResultRead]:
    redis = Redis(host=os.getenv('REDIS_HOST'), password=os.getenv('REDIS_PASSWORD'))
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
