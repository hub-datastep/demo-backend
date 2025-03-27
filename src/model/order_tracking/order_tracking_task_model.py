from fastapi import HTTPException, status
from loguru import logger
from sqlmodel import Session

from infra.database import engine
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


def start_order_tracking(
    config_id: int,
    order_id: int,
) -> OrderTrackingTask | None:
    with Session(engine) as session:
        db_task = order_tracking_task_repository.get_by_order_id(
            session=session,
            order_id=order_id,
        )

        if not db_task:
            task = OrderTrackingTask(
                config_id=config_id,
                order_id=order_id,
            )
            return order_tracking_task_repository.create(
                session=session,
                task=task,
            )
        else:
            logger.error(f"Order with ID {order_id} alreading on tracking")
