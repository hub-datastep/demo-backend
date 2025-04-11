from fastapi import HTTPException, status
from sqlmodel import Session

from model.base import BaseModel
from repository.order_classification.order_classification_config_repository import (
    DEFAULT_CONFIG_ID,
    OrderClassificationConfigRepository,
    get_config_by_id,
    get_config_by_user_id,
    get_default_config,
    order_classification_config_repository,
)
from scheme.order_classification.order_classification_config_scheme import (
    OrderClassificationConfig,
)


def get_order_classification_default_config(
    client: str | None = None,
) -> OrderClassificationConfig:

    config = get_default_config(
        client=client,
    )

    # Check if default config exists
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Default order classification config "
                f"(with ID {DEFAULT_CONFIG_ID} and client '{client}') not found"
            ),
        )

    return config


def get_order_classification_config_by_id(
    config_id: int,
) -> OrderClassificationConfig:
    config = get_config_by_id(config_id)

    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order Classification Config with ID {config_id} not found",
        )

    return config


def get_order_classification_config_by_user_id(
    session: Session,
    user_id: int,
) -> OrderClassificationConfig:
    config = get_config_by_user_id(session, user_id)

    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Order Classification Config for user with ID {user_id} not found",
            ),
        )

    return config


class OrderClassificationConfigModel(
    BaseModel[
        OrderClassificationConfig,
        OrderClassificationConfigRepository,
    ]
):
    def __init__(self) -> None:
        super().__init__(
            schema=OrderClassificationConfig,
            repository=order_classification_config_repository,
        )

    async def get_default(
        self,
        client: str | None = None,
    ) -> OrderClassificationConfig:
        config = await self.repository.get_default(client=client)

        # Check if default config exists
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Default order classification config "
                    f"(with ID {DEFAULT_CONFIG_ID} and client '{client}') not found"
                ),
            )

        return config


order_classification_config_model = OrderClassificationConfigModel()
