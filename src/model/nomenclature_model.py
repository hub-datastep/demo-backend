from starlette.datastructures import UploadFile
from rq.queue import Queue
from rq.job import Job
from redis import Redis

from datastep.components import datastep_nomenclature
from dto.nomenclature_mapping_job_dto import NomenclatureMappingJobOutDto, NomenclatureMappingUpdateDto
from infra.supabase import supabase


def parse_file(file_object: UploadFile):
    return [s.decode("utf-8") for s in file_object.file.readlines()]


def parse_string(file: str):
    return file.split("\n")


def create_job(query: str):
    redis = Redis()
    queue = Queue(name="nomenclature", connection=redis)
    print(query)
    queue.enqueue(datastep_nomenclature.do_mapping, query, result_ttl=-1)


def process(nomenclature_object: UploadFile | str | list[str]):
    if isinstance(nomenclature_object, str):
        nomenclatures = parse_string(nomenclature_object)
    elif isinstance(nomenclature_object, UploadFile):
        nomenclatures = parse_file(nomenclature_object)
    else:
        nomenclatures = nomenclature_object

    for nomenclature in nomenclatures:
        create_job(nomenclature)


def update_nomenclature_mapping(body: NomenclatureMappingUpdateDto):
    supabase.table("nomenclature_mapping").update({"correctness": body.correctness}).eq("id", body.id).execute()


def get_jobs_from_rq():
    redis = Redis()
    queue = Queue("nomenclature", connection=redis)

    queued_job_ids = queue.get_job_ids()
    started_job_ids = queue.started_job_registry.get_job_ids()
    failed_job_ids = queue.failed_job_registry.get_job_ids()

    jobs = Job.fetch_many([*queued_job_ids, *started_job_ids, *failed_job_ids], connection=redis)

    result = []
    for job in jobs:
        result.append(NomenclatureMappingJobOutDto(
            id=job.get_meta().get("mapping_id", None),
            input=job.args[0],
            output=job.return_value(),
            status=job.get_status(),
            wide_group=job.get_meta().get("wide_group", None),
            middle_group=job.get_meta().get("middle_group", None),
            narrow_group=job.get_meta().get("narrow_group", None)
        ))

    return result


def get_jobs_from_database():
    response = supabase.table("nomenclature_mapping").select("*").order("id").execute()

    result = []
    for job in response.data:
        result.append(NomenclatureMappingJobOutDto(**job))

    return result


def get_all_jobs() -> list[NomenclatureMappingJobOutDto]:
    jobs_from_rq = get_jobs_from_rq()
    jobs_from_database = get_jobs_from_database()
    return [*jobs_from_rq, *jobs_from_database]


if __name__ == "__main__":
    all_jobs = get_all_jobs()

    for job in all_jobs:
        print(job.get_status(), job.id, job.args)
