from aiohttp import ClientSession
from fastapi import HTTPException

from infra.domyland.constants import DOMYLAND_API_BASE_URL, DOMYLAND_APP_NAME


class DomylandClient:
    auth_token: str | None = None

    def __init__(self, app_name: str) -> None:
        self.base_url = DOMYLAND_API_BASE_URL
        self.app_name = app_name

    @property
    def headers(self) -> dict[str, str]:
        headers = {
            "AppName": self.app_name,
        }

        if self.auth_token:
            headers.update({"Authorization": self.auth_token})

        return headers

    async def request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> dict:
        url = f"{self.base_url}/{endpoint}"

        async with ClientSession() as session:
            response = await session.request(
                method=method,
                url=url,
                headers=self.headers,
                **kwargs,
            )

            if not response.ok:
                error_message = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Domyland API: {error_message}",
                )

            response_data: dict = await response.json()
            return response_data


Domyland = DomylandClient(app_name=DOMYLAND_APP_NAME)
