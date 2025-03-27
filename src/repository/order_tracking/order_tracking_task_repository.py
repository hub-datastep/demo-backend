from sqlmodel import Session, select

from infra.order_tracking.task_status import ORDER_TASK_NOT_TRACKING_STATUSES
from scheme.order_tracking.order_tracking_task_scheme import OrderTrackingTask
from util.dates import get_now_utc


def get_by_id(
    session: Session,
    task_id: int,
) -> OrderTrackingTask | None:
    st = select(OrderTrackingTask)
    st = st.where(OrderTrackingTask.id == task_id)

    result = session.exec(st).first()

    return result


def get_by_order_id(
    session: Session,
    order_id: int,
) -> OrderTrackingTask | None:
    st = select(OrderTrackingTask)
    st = st.where(OrderTrackingTask.order_id == order_id)

    result = session.exec(st).first()

    return result


def get_uncompleted(
    session: Session,
) -> list[OrderTrackingTask]:
    st = select(OrderTrackingTask)
    st = st.where(OrderTrackingTask.is_completed == False)
    st = st.where(OrderTrackingTask.next_action.isnot(None))
    st = st.where(
        OrderTrackingTask.internal_status.notin_(
            ORDER_TASK_NOT_TRACKING_STATUSES,
        ),
    )

    results_list = list(session.exec(st).unique().all())

    return results_list


def create(
    session: Session,
    task: OrderTrackingTask,
) -> OrderTrackingTask:
    task.created_at = get_now_utc()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def update(
    session: Session,
    task: OrderTrackingTask,
) -> OrderTrackingTask:
    db_task = session.merge(task)
    session.commit()
    session.refresh(db_task)
    return db_task
