from fastapi import HTTPException, status
from sqlmodel import Session

from repository.order_tracking import order_tracking_task_repository
from scheme.order_tracking.order_tracking_task_scheme import OrderTrackingTask


def get_by_id(
    session: Session,
    task_id: int,
) -> OrderTrackingTask:
    task = order_tracking_task_repository.get_by_id(
        session=session,
        task_id=task_id,
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order Tracking Task with ID {task_id} not found",
        )

    return task
