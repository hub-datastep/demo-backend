import ast
import json
import os
import uuid

import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from fastapi import HTTPException
from fastembed.embedding import FlagEmbedding
from redis import Redis
from rq import get_current_job
from rq.job import Job
from rq.queue import Queue
from tqdm import tqdm

from scheme.nomenclature_scheme import NomenclaturesUpload, OneNomenclatureRead, OneNomenclatureUpload, \
    NomenclaturesRead, JobIdRead

tqdm.pandas()
np.set_printoptions(threshold=np.inf)


def map_on_group(noms: pd.DataFrame) -> list:
    model = joblib.load(f"{os.getenv('DATA_FOLDER_PATH')}/linear_svc_model_141223.pkl")
    count_vect = joblib.load(f"{os.getenv('DATA_FOLDER_PATH')}/vectorizer_141223.pkl")
    return model.predict(count_vect.transform(noms["nomenclature"]))


def map_on_nom(nom: str, candidates: pd.DataFrame, n=1):
    def cosine_similarity(a, b):
        return np.dot(a, b)
    nom_embeddings = get_embeddings(nom)
    candidates["similarities"] = candidates.embeddings.apply(lambda x: cosine_similarity(nom_embeddings, x))
    res = candidates.sort_values("similarities", ascending=False).head(n)
    return res["nomenclature"].str.cat(sep='\n')


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


def get_embeddings(string: str) -> np.ndarray:
    embedding_model = FlagEmbedding(
        model_name="intfloat/multilingual-e5-large"
    )
    result = list(embedding_model.query_embed([string]))[0]
    return result


def create_job(nomenclatures: NomenclaturesUpload) -> JobIdRead:
    nomenclature_id = uuid.uuid4()
    redis = Redis(host=os.getenv("REDIS_HOST"))
    queue = Queue(name="nomenclature", connection=redis)
    queue.enqueue(
        process,
        nomenclatures.nomenclatures,
        meta={"nomenclature_id": nomenclature_id, "status": "queued"},
        result_ttl=-1,
        job_timeout=3600*24
    )
    return JobIdRead(nomenclature_id=nomenclature_id)


def process(nomenclatures: list[OneNomenclatureUpload]):
    job = get_current_job()

    noms: pd.DataFrame = parse_txt_file(nomenclatures)
    job.meta["total_count"] = len(noms)
    job.meta["ready_count"] = 0
    job.save_meta()

    noms["group"] = map_on_group(noms)
    noms["mapping"] = None

    candidates = get_nom_candidates(noms.group.unique())
    candidates.embeddings = candidates.progress_apply(
        lambda x: get_embeddings(x.nomenclature)
        if len(x.embeddings) == 0
        else x.embeddings,
        axis=1
    )
    # enhance_db_noms_with_embeddings(db, candidates)

    with tqdm(total=len(noms)) as pbar:
        for i, nom in noms.iterrows():
            c = candidates[candidates["group"] == nom.group]
            nom.mapping = map_on_nom(nom.nomenclature, c)
            noms.loc[i] = nom
            job.meta["ready_count"] += 1
            job.save_meta()
            pbar.update()

    job.meta["status"] = "finished"
    job.save_meta()
    return noms.to_json(orient="records")


def get_jobs_from_rq(nomenclature_id: uuid.UUID) -> NomenclaturesRead:
    def get_all_jobs():
        queued_job_ids = queue.get_job_ids()
        started_job_ids = queue.started_job_registry.get_job_ids()
        finished_job_ids = queue.finished_job_registry.get_job_ids()
        failed_job_ids = queue.failed_job_registry.get_job_ids()

        return Job.fetch_many([*queued_job_ids, *started_job_ids, *finished_job_ids, *failed_job_ids], connection=redis)

    redis = Redis(host=os.getenv("REDIS_HOST"))
    queue = Queue("nomenclature", connection=redis)

    jobs = get_all_jobs()

    wanted_jobs = [j for j in jobs if j.get_meta(refresh=True).get("nomenclature_id", None) == nomenclature_id]

    if len(wanted_jobs) == 0:
        raise HTTPException(status_code=404, detail="Такого UUID не существует")

    job = wanted_jobs[0]

    job_meta = job.get_meta()
    job_result = NomenclaturesRead(
        nomenclature_id=nomenclature_id,
        ready_count=job_meta["ready_count"],
        total_count=job_meta["total_count"],
        general_status=job_meta["status"],
        nomenclatures=[]
    )

    if job_meta["status"] == "finished":
        result_json = job.return_value()
        result_dict = json.loads(result_json)
        job_result.nomenclatures = [OneNomenclatureRead(**d, status="finished") for d in result_dict]

    return job_result


def get_all_jobs(nomenclature_id: uuid.UUID) -> NomenclaturesRead:
    jobs_from_rq = get_jobs_from_rq(nomenclature_id)
    return jobs_from_rq


if __name__ == "__main__":
    load_dotenv()
    FlagEmbedding(
        model_name="intfloat/multilingual-e5-large"
    )
    # noms = [OneNomenclatureUpload(row_number=1, nomenclature="Кабель силовой АВВГнг(А)-LS 4х120мс(N)-1 ТРТС"), OneNomenclatureUpload(row_number=1, nomenclature="Кабель силовой ВВГнг(А)-LS 3х1.5-0,660 плоский")]
    # nomenclature_id = create_job(NomenclaturesUpload(nomenclatures=noms))
    # print(get_all_jobs(nomenclature_id))
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(res)
