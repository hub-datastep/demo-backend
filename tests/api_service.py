import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

TESTS_API_URL = os.getenv('TESTS_API_URL')
TEST_MAPPING_MODEL_ID = os.getenv('TEST_MAPPING_MODEL_ID')

# URL для авторизации и API
AUTH_URL = f"{TESTS_API_URL}/auth/sign_in"
API_URL = f"{TESTS_API_URL}/nomenclature/mapping"

# Данные для авторизации
AUTH_PAYLOAD = {
    "grant_type": "password",
    "username": "admin@admin.com",
    "password": "admin",
    "scope": "",
    "client_id": "",
    "client_secret": ""
}

START_NOMENCLATURE_MAPPING_PAYLOAD_CONFIG = {
    "chroma_collection_name": "test_unistroy_nomenclatures",
    "model_id": TEST_MAPPING_MODEL_ID,
    "most_similar_count": 1,
    "chunk_size": 100,
}


def authenticate():
    response = requests.post(AUTH_URL, data=AUTH_PAYLOAD)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception("Authentication failed")


def start_nomenclature_mapping(test_cases, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        **START_NOMENCLATURE_MAPPING_PAYLOAD_CONFIG,
        "nomenclatures": [
            {
                "row_number": idx,
                "nomenclature": case['Номенклатура поставщика']
            } for idx, case in enumerate(test_cases)
        ]
    }

    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json().get("job_id")
    else:
        print(f"Failed to start mapping. Status code: {response.status_code}")
        print(response.text)
        return None


def get_nomenclature_mappings(job_id, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = f"{API_URL}/{job_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(f"Response data: {response.json()}")
        return response.json()
    else:
        print(response.text)
        return None


def wait_for_job_completion(job_id, token, interval=5):
    while True:
        result = get_nomenclature_mappings(job_id, token)
        if result and isinstance(result, list):
            job_info = result[0]  # Предполагаем, что результат - это список с одним элементом
            if job_info.get('general_status') == 'finished':
                return job_info
            elif job_info.get('general_status') == 'failed':
                raise Exception("Job failed")
        time.sleep(interval)
