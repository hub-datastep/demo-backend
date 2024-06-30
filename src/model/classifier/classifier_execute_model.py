import joblib
from pandas import DataFrame

from infra.redis_queue import get_redis_queue, QueueName, MAX_JOB_TIMEOUT, get_job
from model.classifier.classifier_version_model import get_model_path
from scheme.classifier.classifier_version_scheme import ClassificationResultItem, ClassificationResult
from scheme.task.task_scheme import JobIdRead
from util.normalize_name import normalize_name


def get_groups_by_items(items: list[str], model_id: str) -> list[ClassificationResultItem]:
    model_path = get_model_path(model_id)
    model = joblib.load(model_path)
    result: list[ClassificationResultItem] = []

    normalized_data = DataFrame({
        "names": [normalize_name(item) for item in items]
    })
    groups_ids = model.predict(normalized_data['names'])
    for item, group_id in zip(items, groups_ids):
        result.append(ClassificationResultItem(item=item, group_id=group_id))

    return result


def start_classification(items: list[str], model_id: str) -> JobIdRead:
    queue = get_redis_queue(name=QueueName.CLASSIFICATION)
    job = queue.enqueue(
        get_groups_by_items,
        items,
        model_id,
        result_ttl=-1,
        job_timeout=MAX_JOB_TIMEOUT,
    )
    return JobIdRead(job_id=job.id)


def get_classification_job_result(job_id: str) -> ClassificationResult:
    job = get_job(job_id)

    classification_result = ClassificationResult(
        job_id=job_id,
        status=job.get_status(refresh=True)
    )

    job_result = job.return_value(refresh=True)
    if job_result is not None:
        classification_result.result = job_result

    return classification_result
