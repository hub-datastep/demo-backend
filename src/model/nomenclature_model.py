import ast
import typing
import os
from io import StringIO

from tqdm import tqdm
import pandas as pd
import numpy as np
import joblib
from starlette.datastructures import UploadFile
from rq.queue import Queue
from rq.job import Job
from redis import Redis
from fastembed.embedding import FlagEmbedding
from fastapi import HTTPException

from dto.nomenclature_mapping_job_dto import NomenclatureMappingJobDto, NomenclatureMappingDto

tqdm.pandas()
np.set_printoptions(threshold=np.inf)


def parse_file(file_object: UploadFile):
    return [s.decode("utf-8").strip() for s in file_object.file.readlines()], file_object.filename


def map_on_group(noms: pd.DataFrame) -> list:
    model = joblib.load(f"{os.getcwd()}/data/linear_svc_model_141223.pkl")
    count_vect = joblib.load(f"{os.getcwd()}/data/vectorizer_141223.pkl")
    return model.predict(count_vect.transform(noms["nomenclature"]))


def map_on_nom(nom: str, candidates: pd.DataFrame, n=1):
    def cosine_similarity(a, b):
        return np.dot(a, b)
    nom_embeddings = get_embeddings(nom)
    candidates["similarities"] = candidates.embeddings.apply(lambda x: cosine_similarity(nom_embeddings, x))
    res = candidates.sort_values("similarities", ascending=False).head(n)
    return res["nomenclature"].str.cat(sep='\n')


def parse_txt_file(file: typing.BinaryIO) -> pd.DataFrame:
    return pd.read_csv(file, names=["nomenclature"], sep=";")


def get_nom_candidates(db: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    candidates = db[db["group"].isin(groups)]
    candidates = candidates.replace({np.nan: "[]"})
    candidates.embeddings = candidates.embeddings.progress_apply(ast.literal_eval).progress_apply(np.array)
    return candidates


def enhance_db_noms_with_embeddings(db: pd.DataFrame, candidates: pd.DataFrame):
    c = candidates.copy()
    c.embeddings = c.embeddings.progress_apply(lambda x: np.array2string(x, separator=","))
    db.update(c)


def get_embeddings(string: str) -> np.ndarray:
    embedding_model = FlagEmbedding(model_name="intfloat/multilingual-e5-large")
    result = list(embedding_model.query_embed([string]))[0]
    return result


def create_job(nomenclature_object: UploadFile | str):
    if not nomenclature_object.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Поддерживается только .txt")
    redis = Redis()
    queue = Queue(name="nomenclature", connection=redis)
    job = queue.enqueue(process, nomenclature_object, result_ttl=-1, job_timeout=3600)
    job.meta["source"] = nomenclature_object.filename
    job.save_meta()


def process(nomenclature_object: UploadFile | str):
    db = pd.read_csv(f"{os.getcwd()}/data/msudb_full_221223.csv", sep=";")

    if type(nomenclature_object) is str:
        file = StringIO(nomenclature_object)
    else:
        file = nomenclature_object.file
    noms: pd.DataFrame = parse_txt_file(file)
    noms["group"] = map_on_group(noms)
    noms["mapping"] = None

    candidates = get_nom_candidates(db, noms.group.unique())
    candidates.embeddings = candidates.progress_apply(
        lambda x: get_embeddings(x.nomenclature)
        if len(x.embeddings) == 0
        else x.embeddings,
        axis=1
    )
    enhance_db_noms_with_embeddings(db, candidates)
    db.to_csv(f"{os.getcwd()}/data/msudb_full_221223.csv", sep=";")

    with tqdm(total=len(noms)) as pbar:
        for i, nom in noms.iterrows():
            c = candidates[candidates["group"] == nom.group]
            nom.mapping = map_on_nom(nom.nomenclature, c)
            noms.loc[i] = nom
            pbar.update()

    noms.to_csv(f"{os.getcwd()}/data/{nomenclature_object.filename.replace('.txt', '')}_result.csv")


def get_jobs_from_rq(source: str | None) -> list[NomenclatureMappingJobDto]:
    redis = Redis()
    queue = Queue("nomenclature", connection=redis)

    queued_job_ids = queue.get_job_ids()
    started_job_ids = queue.started_job_registry.get_job_ids()
    finished_job_ids = queue.finished_job_registry.get_job_ids()
    failed_job_ids = queue.failed_job_registry.get_job_ids()

    jobs = Job.fetch_many([*queued_job_ids, *started_job_ids, *finished_job_ids, *failed_job_ids], connection=redis)

    result = []
    wanted_jobs = [j for j in jobs if j.get_meta().get("source", None) == source]

    for job in wanted_jobs:
        job_dto = NomenclatureMappingJobDto(
            source=job.get_meta().get("source", None),
            status=job.get_status(),
        )

        if job.get_status() == "finished":
            mappings = [
                NomenclatureMappingDto(
                    nomenclature=m["nomenclature"],
                    group=m["group"],
                    mapping=m["mapping"]
                ) for m in pd.read_csv(f"{os.getcwd()}/data/{source.replace('.txt', '')}_result.csv").to_dict("records")
            ]
            job_dto.mappings = mappings

        result.append(job_dto)

    return result


def get_all_jobs(source: str | None) -> list[NomenclatureMappingJobDto]:
    jobs_from_rq = get_jobs_from_rq(source)
    return jobs_from_rq


if __name__ == "__main__":
    tqdm.pandas()
    np.set_printoptions(threshold=np.inf)
    process("Мусороствол СМП-ПП 3-сл. D=400мм с отв. для КМЗ, L=1490мм, без окраш., ГалВент")
    with open("jms_artem_test_131223_1.txt") as f:
        process(f.read())
