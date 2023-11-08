from starlette.datastructures import UploadFile
from rq.queue import Queue
from rq.job import Job
from redis import Redis

from datastep.components import datastep_nomenclature
from dto.nomenclature_mapping_job_dto import NomenclatureMappingJobOutDto, NomenclatureMappingUpdateDto
from infra.supabase import supabase


def parse_file(file_object: UploadFile):
    return [s.decode("utf-8") for s in file_object.file.readlines()], file_object.filename


def parse_string(file: str):
    return file.split("\n")


def create_job(query: str, filename: str | None):
    redis = Redis()
    queue = Queue(name="nomenclature", connection=redis)
    job = queue.enqueue(datastep_nomenclature.do_mapping, query, result_ttl=-1)
    job.meta["source"] = filename
    job.save_meta()


def process(nomenclature_object: UploadFile):
    nomenclatures, filename = parse_file(nomenclature_object)

    for nomenclature in nomenclatures:
        create_job(nomenclature, filename)


def update_nomenclature_mapping(body: NomenclatureMappingUpdateDto):
    supabase.table("nomenclature_mapping").update({"correctness": body.correctness}).eq("id", body.id).execute()


def get_jobs_from_rq(source: str | None):
    redis = Redis()
    queue = Queue("nomenclature", connection=redis)

    queued_job_ids = queue.get_job_ids()
    started_job_ids = queue.started_job_registry.get_job_ids()
    failed_job_ids = queue.failed_job_registry.get_job_ids()

    jobs = Job.fetch_many([*queued_job_ids, *started_job_ids, *failed_job_ids], connection=redis)

    result = []
    wanted_jobs = [j for j in jobs if j.get_meta().get("source", None) == source]
    for job in wanted_jobs:
        result.append(NomenclatureMappingJobOutDto(
            id=job.get_meta().get("mapping_id", None),
            input=job.args[0],
            output=job.return_value(),
            source=job.get_meta().get("source", None),
            status=job.get_status(),
            wide_group=job.get_meta().get("wide_group", None),
            middle_group=job.get_meta().get("middle_group", None),
            narrow_group=job.get_meta().get("narrow_group", None),
        ))

    return result


def get_jobs_from_database(source: str | None):
    response = supabase.table("nomenclature_mapping").select("*").order("id").eq("source", source).execute()

    result = []
    for job in response.data:
        result.append(NomenclatureMappingJobOutDto(**job))

    return result


def get_all_jobs(source: str | None) -> list[NomenclatureMappingJobOutDto]:
    jobs_from_rq = get_jobs_from_rq(source)
    jobs_from_database = get_jobs_from_database(source)
    return [*jobs_from_rq, *jobs_from_database]


if __name__ == "__main__":
    all_jobs = get_all_jobs("source.txt")

    for job in all_jobs:
        print(job.get_status(), job.id, job.args)
