import ast
import json
import os

import joblib
import numpy as np
import pandas as pd
from chromadb import HttpClient
from fastembed.embedding import FlagEmbedding
from redis import Redis
from rq import get_current_job
from rq.job import Job, JobStatus
from rq.queue import Queue
from tqdm import tqdm

from scheme.nomenclature_scheme import NomenclaturesUpload, OneNomenclatureRead, OneNomenclatureUpload, \
    NomenclaturesRead, JobIdRead, MappedNomenclature

tqdm.pandas()
np.set_printoptions(threshold=np.inf)


def map_on_group(noms: pd.DataFrame) -> list:
    model = joblib.load(f"{os.getenv('DATA_FOLDER_PATH')}/linear_svc_model_141223.pkl")
    count_vect = joblib.load(f"{os.getenv('DATA_FOLDER_PATH')}/vectorizer_141223.pkl")
    return model.predict(count_vect.transform(noms["nomenclature"]))


def map_on_nom(nom_embeddings: np.ndarray, group: str, most_similar_count: int):
    chroma = HttpClient(host=os.getenv("CHROMA_HOST"), port=os.getenv("CHROMA_PORT"))
    collection = chroma.get_collection(name="nomenclature")

    nom_embeddings = nom_embeddings.tolist()
    response = collection.query(
        query_embeddings=[nom_embeddings],
        n_results=most_similar_count,
        where={"group": group}
    )

    mapped_noms = []
    for i in range(most_similar_count):
        mapped_noms.append(MappedNomenclature(
            nomenclature_guid=response["ids"][i],
            nomenclature=response["documents"][i],
            similarity_score=response["distances"][i],
        ))
    # Sort from most similar to lower
    mapped_noms.sort(key=lambda nom: nom.similarity_score, reverse=True)

    return mapped_noms


def parse_txt_file(nomenclatures: list[OneNomenclatureUpload]) -> pd.DataFrame:
    nomenclatures_as_json = [n.dict().values() for n in nomenclatures]
    return pd.DataFrame(nomenclatures_as_json, columns=["row_number", "nomenclature"])


def get_nom_candidates(groups: list[str]) -> pd.DataFrame:
    groups_str = ", ".join([f"'{g}'" for g in groups])
    candidates = pd.read_sql(
        f'SELECT * FROM nomenclature WHERE "group" in ({groups_str})',
        os.getenv("DB_CONNECTION_STRING")
    )
    candidates = candidates.replace({np.nan: "[]"})
    candidates.embeddings = candidates.embeddings.progress_apply(ast.literal_eval).progress_apply(np.array)
    return candidates


# def enhance_db_noms_with_embeddings(db: pd.DataFrame, candidates: pd.DataFrame):
#     c = candidates.copy()
#     c.embeddings = c.embeddings.progress_apply(lambda x: np.array2string(x, separator=","))
#     db.update(c)


def get_embeddings(strings: list[str]) -> list[np.ndarray]:
    embedding_model = FlagEmbedding(
        model_name="intfloat/multilingual-e5-large"
    )
    strings = [f"query: {s}" for s in strings]
    result = list(embedding_model.embed(strings))
    return result


def nomenclature_segments(
    nomenclatures: list[OneNomenclatureUpload],
    segment_length: int = 100
) -> list[list[OneNomenclatureUpload]]:
    # https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks
    for i in range(0, len(nomenclatures), segment_length):
        yield nomenclatures[i:i + segment_length]


def create_job(
    nomenclatures: list[OneNomenclatureUpload],
    previous_job_id: str | None,
    most_similar_count: int
) -> JobIdRead:
    redis = Redis(host=os.getenv("REDIS_HOST"), password=os.getenv("REDIS_PASSWORD"))
    queue = Queue(name="nomenclature", connection=redis)
    job = queue.enqueue(
        process,
        nomenclatures,
        most_similar_count,
        meta={
            "previous_nomenclature_id": previous_job_id
        },
        result_ttl=-1,
        job_timeout=3600 * 24
    )
    return JobIdRead(job_id=job.id)


def start_mapping(nomenclatures: NomenclaturesUpload) -> JobIdRead:
    nomenclatures_list = nomenclatures.nomenclatures
    most_similar_count = nomenclatures.most_similar_count

    last_job_id = None
    for segment in nomenclature_segments(nomenclatures_list, segment_length=nomenclatures.job_size):
        job = create_job(
            nomenclatures=segment,
            previous_job_id=last_job_id,
            most_similar_count=most_similar_count
        )
        last_job_id = job.job_id

    return JobIdRead(job_id=last_job_id)


def process(nomenclatures: list[OneNomenclatureUpload], most_similar_count: int):
    job = get_current_job()

    noms: pd.DataFrame = parse_txt_file(nomenclatures)
    job.meta["total_count"] = len(noms)
    job.meta["ready_count"] = 0
    job.save_meta()

    noms["group"] = map_on_group(noms)
    noms["mapping"] = None

    # enhance_db_noms_with_embeddings(db, candidates)

    noms["embeddings"] = get_embeddings(noms.nomenclature.to_list())

    with tqdm(total=len(noms)) as pbar:
        for i, nom in noms.iterrows():
            nom.mapping = map_on_nom(nom.embeddings, nom.group, most_similar_count)
            noms.loc[i] = nom
            job.meta["ready_count"] += 1
            job.save_meta()
            pbar.update()

    job.meta["status"] = "finished"
    job.save_meta()
    return noms.to_json(orient="records", force_ascii=False)


def get_jobs_from_rq(nomenclature_id: str) -> list[NomenclaturesRead]:
    redis = Redis(host=os.getenv("REDIS_HOST"), password=os.getenv("REDIS_PASSWORD"))
    jobs_list: list[NomenclaturesRead] = []

    prev_job_id = nomenclature_id
    while prev_job_id is not None:
        job = Job.fetch(prev_job_id, connection=redis)
        job_meta = job.get_meta(refresh=True)
        job_status = job.get_status(refresh=True)
        job_result = NomenclaturesRead(
            job_id=job.id,
            ready_count=job_meta.get("ready_count", None),
            total_count=job_meta.get("total_count", None),
            general_status=job_status,
            nomenclatures=[]
        )

        if job_status == JobStatus.FINISHED:
            result_json = job.return_value()
            result_dict = json.loads(result_json)
            job_result.nomenclatures = [OneNomenclatureRead(**d) for d in result_dict]

        jobs_list.append(job_result)
        prev_job_id = job_meta["previous_nomenclature_id"]

    return jobs_list


def get_all_jobs(nomenclature_id: str) -> list[NomenclaturesRead]:
    jobs_from_rq = get_jobs_from_rq(nomenclature_id)
    return jobs_from_rq


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    # from dotenv import load_dotenv
    #
    # load_dotenv()
    # FlagEmbedding(
    #     model_name="intfloat/multilingual-e5-large"
    # )
    noms = [
        OneNomenclatureUpload(row_number=1, nomenclature="Кабель силовой АВВГнг(А)-LS 4х120мс(N)-1 ТРТС"),
        OneNomenclatureUpload(row_number=1, nomenclature="Кабель силовой ВВГнг(А)-LS 3х1.5-0,660 плоский"),
        OneNomenclatureUpload(row_number=1, nomenclature="Кабель силовой ВВГнг(А)-LS 3х1.5-0,660 плоский"),
        OneNomenclatureUpload(row_number=1, nomenclature="Кабель силовой ВВГнг(А)-LS 3х1.5-0,660 плоский"),
        OneNomenclatureUpload(row_number=1, nomenclature="Кабель силовой ВВГнг(А)-LS 3х1.5-0,660 плоский"),
        OneNomenclatureUpload(row_number=1, nomenclature="Кабель силовой ВВГнг(А)-LS 3х1.5-0,660 плоский"),
        OneNomenclatureUpload(row_number=1, nomenclature="Кабель силовой ВВГнг(А)-LS 3х1.5-0,660 плоский"),
        OneNomenclatureUpload(row_number=1, nomenclature="Кабель силовой ВВГнг(А)-LS 3х1.5-0,660 плоский"),
        OneNomenclatureUpload(row_number=1, nomenclature="Кабель силовой ВВГнг(А)-LS 3х1.5-0,660 плоский"),
        OneNomenclatureUpload(row_number=1, nomenclature="Кабель силовой ВВГнг(А)-LS 3х1.5-0,660 плоский")
    ]
    result = process(noms)
    # for open("file.txt", "w") as f:
    #     f.write(result)
    # print(result, encoding)
    # pprint.pprint(result)
    # print(get_all_jobs(nomenclature_id))
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(res)

    pass
