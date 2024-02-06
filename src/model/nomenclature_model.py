import ast
import json
import os

import joblib
import numpy as np
import pandas as pd
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
    # candidates["similarities"] = candidates.embeddings.apply(lambda x: cosine_similarity(nom_embeddings, x))
    # res = candidates.sort_values("similarities", ascending=False).head(n)
    # return res["nomenclature"].str.cat(sep='\n')
    similarities = candidates.embeddings.apply(lambda x: cosine_similarity(nom_embeddings, x))
    res = candidates.iloc[np.argsort(similarities)[-n:]].sort_values("similarities", ascending=False)
    return '\n'.join(res["nomenclature"])


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


def split_nomenclatures_by_segments(
    nomenclatures: list[OneNomenclatureUpload],
    segment_length: int = 300
) -> list[list[OneNomenclatureUpload]]:
    segments: list[list[OneNomenclatureUpload]] = []
    for i in range(segment_length, len(nomenclatures) + segment_length, segment_length):
        segments.append(nomenclatures[i - segment_length: i])

    return segments


def create_job(nomenclatures: list[OneNomenclatureUpload], previous_job_id: str | None) -> JobIdRead:
    redis = Redis(host=os.getenv("REDIS_HOST"))
    queue = Queue(name="nomenclature", connection=redis)
    job = queue.enqueue(
        process,
        nomenclatures,
        meta={
            "status": "queued",
            "previous_nomenclature_id": previous_job_id
        },
        result_ttl=-1,
        job_timeout=3600 * 24
    )
    return JobIdRead(nomenclature_id=job.id)


def start_mapping(nomenclatures: NomenclaturesUpload) -> JobIdRead:
    nomenclatures_list = nomenclatures.nomenclatures
    nomenclatures_segments = split_nomenclatures_by_segments(nomenclatures_list)

    last_nomenclature_id = None
    for segment in nomenclatures_segments:
        job = create_job(
            nomenclatures=segment,
            previous_job_id=last_nomenclature_id
        )
        last_nomenclature_id = job.nomenclature_id

    return JobIdRead(nomenclature_id=last_nomenclature_id)


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


def get_jobs_from_rq(nomenclature_id: str) -> list[NomenclaturesRead]:
    redis = Redis(host=os.getenv("REDIS_HOST"))
    jobs_list: list[NomenclaturesRead] = []

    prev_job_id = nomenclature_id
    while prev_job_id is not None:
        job = Job.fetch(prev_job_id, connection=redis)
        job_meta = job.get_meta()
        job_result = NomenclaturesRead(
            nomenclature_id=job.id,
            ready_count=job_meta["ready_count"],
            total_count=job_meta["total_count"],
            general_status=job_meta["status"],
            nomenclatures=[]
        )

        if job_meta["status"] == "finished":
            result_json = job.return_value()
            result_dict = json.loads(result_json)
            job_result.nomenclatures = [OneNomenclatureRead(**d, status="finished") for d in result_dict]

        jobs_list.append(job_result)
        prev_job_id = job_meta["previous_nomenclature_id"]

    return jobs_list


def get_all_jobs(nomenclature_id: str) -> list[NomenclaturesRead]:
    jobs_from_rq = get_jobs_from_rq(nomenclature_id)
    return jobs_from_rq


if __name__ == "__main__":
    # from dotenv import load_dotenv
    #
    # load_dotenv()
    # FlagEmbedding(
    #     model_name="intfloat/multilingual-e5-large"
    # )
    # noms = [OneNomenclatureUpload(row_number=1, nomenclature="Кабель силовой АВВГнг(А)-LS 4х120мс(N)-1 ТРТС"), OneNomenclatureUpload(row_number=1, nomenclature="Кабель силовой ВВГнг(А)-LS 3х1.5-0,660 плоский")]
    # nomenclature_id = create_job(NomenclaturesUpload(nomenclatures=noms))
    # print(get_all_jobs(nomenclature_id))
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(res)

    pass
