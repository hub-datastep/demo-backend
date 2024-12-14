import time

from model.mapping import mapping_model
from scheme.classifier.classifier_config_scheme import ClassifierConfig
from scheme.mapping.mapping_scheme import MappingOneNomenclatureUpload, MappingNomenclaturesResultRead

WAIT_RESULTS_TIME_IN_SEC = 30


def get_noms_with_indexes(nomenclatures_list: list[str]):
    nomenclatures_list_with_indexes = [
        MappingOneNomenclatureUpload(
            row_number=i + 1,
            nomenclature=nom,
        ) for i, nom in enumerate(nomenclatures_list)
    ]
    return nomenclatures_list_with_indexes


def _wait_until_results_finish(job_id: str):
    while True:
        results_list = mapping_model.get_all_jobs(job_id=job_id)
        is_all_jobs_finished = all(
            mapping_model.is_job_finished(nom_result.general_status)
            for nom_result in results_list
        )

        if is_all_jobs_finished:
            return results_list

        time.sleep(WAIT_RESULTS_TIME_IN_SEC)


def start_mapping_and_wait_results(
    nomenclatures_list: list[MappingOneNomenclatureUpload],
    classifier_config: ClassifierConfig,
    tenant_id: int,
    most_similar_count: int = 3,
    chunk_size: int = 100,
) -> list[MappingNomenclaturesResultRead]:
    job = mapping_model.start_mapping(
        nomenclatures=nomenclatures_list,
        most_similar_count=most_similar_count,
        chunk_size=chunk_size,
        classifier_config=classifier_config,
        tenant_id=tenant_id,
    )
    job_id = job.job_id

    results_list = _wait_until_results_finish(job_id=job_id)

    return results_list
