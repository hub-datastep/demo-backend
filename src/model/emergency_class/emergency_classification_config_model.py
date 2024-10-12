from fastapi import HTTPException, status
from sqlmodel import Session

from repository.emergency_class.emergency_classification_config_repository import get_config_by_user_id
from scheme.emergency_class.emergency_classification_config_scheme import EmergencyClassificationConfig


def get_emergency_classification_config_by_user_id(
    session: Session,
    user_id: int,
) -> EmergencyClassificationConfig:
    config = get_config_by_user_id(session, user_id)

    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emergency classification config for user with ID {user_id} not found",
        )

    return config
