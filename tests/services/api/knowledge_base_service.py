import requests

from configs.env import env
from scheme.prediction.prediction_scheme import PredictionQueryBase, KnowledgeBasePredictionRead
from services.api.auth_service import get_auth_headers

_API_URL = env.get_api_route_url(route=f"chat_knowledge_base/prediction")


def start_knowledge_base_prediction(
    test_cases: list[dict],
) -> list[KnowledgeBasePredictionRead] | None:
    headers = get_auth_headers()

    responses: list[KnowledgeBasePredictionRead] = []
    for case in test_cases:
        payload = PredictionQueryBase(
            query=case['Вопрос'],
        )

        response = requests.post(
            url=_API_URL,
            json=payload.dict(),
            headers=headers,
        )

        if not response.ok:
            raise Exception(
                f"Failed to start knowledge base prediction. "
                f"Status code: {response.status_code}. "
                f"Response: {response.text}."
            )

        response_data = KnowledgeBasePredictionRead(**response.json())
        responses.append(response_data)

    return responses
