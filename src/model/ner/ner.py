import httpx
from loguru import logger

from infra.env import env


class NERServiceClient:
    def __init__(self, url: str = env.NER_SERVICE_URL, chunk_size: int = 100, timeout: int = 100):
        self._client = httpx.Client()
        self._chunk_size = chunk_size
        self._timeout = timeout
        self._url = url

    def predict(self, nomenclatures: list[str]) -> list[str]:
        noms_brands_list = []

        nomenclatures_count = len(nomenclatures)
        print(f"Nomenclatures count: {nomenclatures_count}")
        for i in range(0, nomenclatures_count, self._chunk_size):
            noms_chunk = nomenclatures[i:i + self._chunk_size]
            logger.debug(f"Noms chunk: {noms_chunk}")
            logger.debug(f"Noms chunk length: {len(noms_chunk)}")

            if len(noms_chunk) == 0:
                continue

            try:
                body = {
                    "nomenclatures": noms_chunk,
                }
                response = self._client.post(
                    url=self._url,
                    json=body,
                    timeout=self._timeout,
                )
                response_json = response.json()
                response_brands = response_json['brands']
                noms_brands_list.extend(response_brands)

            except Exception as e:
                print(f"Index chunk {i} - {e}")

        logger.debug(f"Nomenclatures brands count: {len(noms_brands_list)}")
        return noms_brands_list

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.close()


ner_service = NERServiceClient()
