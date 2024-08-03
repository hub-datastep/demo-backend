from fastapi import HTTPException, status
from sqlmodel import Session

from repository.mode import mode_repository
from scheme.mode.mode_scheme import Mode


def get_mode_by_id(session: Session, mode_id: int) -> Mode:
    mode = mode_repository.get_mode_by_id(session, mode_id)

    if mode is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mode with ID {mode_id} is not found.",
        )

    return mode
