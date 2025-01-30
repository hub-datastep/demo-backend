import time

import requests
from loguru import logger

from configs.env import env
from model.mapping import mapping_model
from scheme.mapping.mapping_scheme import (
    MappingNomenclaturesUpload, MappingOneNomenclatureUpload,
    MappingNomenclaturesResultRead, MappingOneNomenclatureRead,
)
from scheme.task.task_scheme import JobIdRead
from services.api.auth_service import get_auth_headers

_API_URL = env.get_api_route_url(route=f"mapping")

_PAYLOAD = {
    "most_similar_count": 3,
    "chunk_size": 100,
}


def start_mapping(test_cases: list[dict]) -> JobIdRead:
    headers = get_auth_headers()

    payload = MappingNomenclaturesUpload(
        **_PAYLOAD,
        nomenclatures=[
            MappingOneNomenclatureUpload(
                row_number=idx,
                nomenclature=case['Номенклатура на Вход'],
            ) for idx, case in enumerate(test_cases)
        ],
    )

    response = requests.post(
        url=_API_URL,
        json=payload.dict(),
        headers=headers,
    )

    if not response.ok:
        raise Exception(
            f"Failed to start mapping. "
            f"Status code: {response.status_code}. "
            f"Response: {response.text}."
        )

    job = JobIdRead(**response.json())
    return job


def get_mapping_results(
    job_id: str,
    is_verbose: bool = False,
):
    headers = get_auth_headers()

    response = requests.get(
        url=f"{_API_URL}/{job_id}",
        headers=headers,
    )

    if not response.ok:
        logger.debug(f"Failed to get mapping results")
        logger.debug(f"Status code: {response.status_code}")
        logger.debug(f"Response: {response.text}")
        return None

    results_list = [MappingNomenclaturesResultRead(**data) for data in response.json()]
    logger.info(f"Mapping status: {results_list[0].general_status}")

    if is_verbose:
        for result in results_list:
            logger.info(f"Mapping job id: {result.job_id}")
            logger.info(f"Mapping status: {result.general_status}")
            logger.info(f"Mapping ready count: {result.ready_count}")
            logger.info(f"Mapping total count: {result.total_count}")
            logger.info("")

    return results_list


def wait_for_job_completion(
    job_id: str,
    interval: float = 30,
) -> list[MappingOneNomenclatureRead]:
    # Minimal interval is 30 sec
    interval = max(interval, 30)

    while True:
        results_list = get_mapping_results(job_id=job_id)
        if results_list and isinstance(results_list, list):
            is_all_jobs_finished = all(
                mapping_model.is_job_finished(result.general_status)
                for result in results_list
            )

            if is_all_jobs_finished:
                results: list[MappingOneNomenclatureRead] = []
                for result in results_list:
                    result: MappingNomenclaturesResultRead
                    results.extend(result.nomenclatures)

                return results

        time.sleep(interval)
