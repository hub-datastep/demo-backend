import time

import requests
from loguru import logger
from rq.job import JobStatus

from configs.env import TESTS_API_URL

API_URL = f"{TESTS_API_URL}/mapping"

START_NOMENCLATURE_MAPPING_PAYLOAD_CONFIG = {
    "most_similar_count": 3,
    "chunk_size": 100,
}


def start_nomenclature_mapping(test_cases, token: str):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        **START_NOMENCLATURE_MAPPING_PAYLOAD_CONFIG,
        "nomenclatures": [
            {
                "row_number": idx,
                "nomenclature": case['Номенклатура на Вход']
            } for idx, case in enumerate(test_cases)
        ]
    }

    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json().get("job_id")
    else:
        logger.info(f"Failed to start mapping")
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Response: {response.text}")
        return None


def get_nomenclature_mappings(
    job_id: str,
    token: str,
    is_verbose: bool = False,
):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = f"{API_URL}/{job_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        response_datas = response.json()
        logger.info(f"Mapping status: {response_datas[0]['general_status']}")
        if is_verbose:
            for mapping_results in response_datas:
                logger.info(f"Mapping job id: {mapping_results['job_id']}")
                logger.info(f"Mapping status: {mapping_results['general_status']}")
                logger.info(f"Mapping ready count: {mapping_results['ready_count']}")
                logger.info(f"Mapping total count: {mapping_results['total_count']}")
                logger.info("")
        return response_datas
    else:
        logger.info(f"Failed to get mapping results")
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Response: {response.text}")
        return None


def wait_for_job_completion(job_id: str, token: str, interval: float = 30):
    # Minimal interval is 30 sec
    interval = max(interval, 30)

    while True:
        result = get_nomenclature_mappings(job_id, token)
        if result and isinstance(result, list):
            job_info = result[0]

            if job_info['general_status'] == JobStatus.FINISHED:
                result_nomenclatures = []
                for job in result:
                    result_nomenclatures.extend(job['nomenclatures'])

                return result_nomenclatures

            elif job_info['general_status'] == JobStatus.FAILED:
                raise Exception("Job failed")

        time.sleep(interval)
