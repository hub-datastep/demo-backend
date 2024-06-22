import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

TESTS_API_URL = os.getenv('TESTS_API_URL')

# URL для авторизации и API
AUTH_URL = f"{TESTS_API_URL}/auth/sign_in"
API_URL = f"{TESTS_API_URL}/chat_knowledge_base/prediction"

# Данные для авторизации
AUTH_PAYLOAD_LOCAL = {
    "grant_type": "password",
    "username": "admin@admin.com",
    "password": "admin",
    "scope": "",
    "client_id": "",
    "client_secret": ""
}

AUTH_PAYLOAD_PROD = {
    "grant_type": "password",
    "username": "stroy_control",
    "password": "1234567890",
    "scope": "",
    "client_id": "",
    "client_secret": ""
}


def authenticate():
    response = requests.post(AUTH_URL, data=AUTH_PAYLOAD_LOCAL)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception("Authentication failed")


def start_knowledge_base_prediction(test_cases, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    responses = []

    for case in test_cases:
        payload = {
            "query": case['Вопрос']
        }

        response = requests.post(API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            responses.append(response.json())
        else:
            print(f"Failed to start knowledge base prediction. Status code: {response.status_code}")
            return None
    return responses
