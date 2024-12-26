from fastapi import HTTPException, status
from sqlmodel import Session

from repository.order_classification.order_classification_config_repository import get_config_by_user_id, \
    get_config_by_id
from scheme.order_classification.order_classification_config_scheme import OrderClassificationConfig


def get_order_classification_config_by_id(
    session: Session,
    config_id: int,
) -> OrderClassificationConfig:
    config = get_config_by_id(session, config_id)

    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emergency classification config with ID {config_id} not found",
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
            detail=f"Emergency classification config for user with ID {user_id} not found",
        )

    return config
