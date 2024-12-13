import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()
class Mapping:
    def __init__(self, noms):
        self.TESTS_API_URL = os.getenv('TESTS_API_URL')
        self.TEST_MAPPING_USERNAME = os.getenv('TEST_MAPPING_USERNAME')
        self.TEST_MAPPING_PASSWORD = os.getenv('TEST_MAPPING_PASSWORD')

        # URL для авторизации и API
        self.AUTH_URL = f"{self.TESTS_API_URL}/auth/sign_in/"
        self.API_URL = f"{self.TESTS_API_URL}/mapping"

        # Данные для авторизации
        self.AUTH_PAYLOAD = {
            "grant_type": "password",
            "username": self.TEST_MAPPING_USERNAME,
            "password": self.TEST_MAPPING_PASSWORD,
        }

        self.START_NOMENCLATURE_MAPPING_PAYLOAD_CONFIG = {
            "most_similar_count": 3,
            "chunk_size": 100,
        }
        self.job_id = ""
        self.token = ""
        self.test_cases = noms


    def authenticate(self):
        response = requests.post(self.AUTH_URL, data=self.AUTH_PAYLOAD)
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            raise Exception("Authentication failed")


    def start_nomenclature_mapping(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        payload = {
            **self.START_NOMENCLATURE_MAPPING_PAYLOAD_CONFIG,
            "nomenclatures": [
                {
                    "row_number": idx,
                    "nomenclature": case
                } for idx, case in enumerate(self.test_cases)
            ]
        }

        response = requests.post(self.API_URL, json=payload, headers=headers) 

        if response.status_code == 200:
            self.job_id = response.json().get("job_id")
        else:
            raise f"Failed to start mapping. Status code: {response.text}"


    def get_nomenclature_mappings(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        url = f"{self.API_URL}/{self.job_id}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_datas = response.json()
            return response_datas
        else:
            print(response.text)
            return None


    def wait_for_job_completion(self, interval: int = 5):
        while True:
            result = self.get_nomenclature_mappings()
            if result and isinstance(result, list):
                job_info = result[0]  # Предполагаем, что результат - это список с одним элементом
                if job_info.get('general_status') == 'finished':
                    return job_info
                elif job_info.get('general_status') == 'failed':
                    raise Exception("Job failed")
            time.sleep(interval)

    def execute(self):
        self.authenticate()
        print('authenticate')
        self.start_nomenclature_mapping()
        print('start_nomenclature_mapping')
        self.wait_for_job_completion()
        print('finish_nomenclature_mapping')
        return self.get_nomenclature_mappings()

if __name__ == "__main__":
    noms = '''Труба ПЭ100 SDR11 - 200х18,2 питьевая (12м)
Лестничный марш ЛМФ 30-11-14,5'''.split('\n')
    
    ans = Mapping(noms).execute()
    print(ans)