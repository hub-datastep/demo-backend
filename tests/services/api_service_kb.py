import requests

from configs.env import TESTS_API_URL

API_URL = f"{TESTS_API_URL}/chat_knowledge_base/prediction"


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
