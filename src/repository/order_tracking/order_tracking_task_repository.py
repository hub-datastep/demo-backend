from sqlmodel import Session, select

from infra.database import engine
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


def get_uncompleted() -> list[OrderTrackingTask]:
    with Session(engine) as session:
        st = select(OrderTrackingTask)
        st = st.where(OrderTrackingTask.is_completed.isnot(True))
        st = st.where(OrderTrackingTask.next_action.isnot(None))
        st = st.where(
            OrderTrackingTask.internal_status.notin_(
                ORDER_TASK_NOT_TRACKING_STATUSES,
            ),
        )
        st = st.order_by(OrderTrackingTask.created_at.asc())

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


def update(task: OrderTrackingTask) -> OrderTrackingTask:
    with Session(engine) as session:
        db_task = session.merge(task)
        session.commit()
        session.refresh(db_task)
        return db_task


from repository.base import BaseRepository


class OrderTrackingTaskRepository(BaseRepository[OrderTrackingTask]):
    """
    Repository for OrderTrackingTask DB table.
    """

    def __init__(self) -> None:
        super().__init__(schema=OrderTrackingTask)

    async def get_uncompleted(self) -> list[OrderTrackingTask]:
        async with self.get_session() as session:
            st = select(self.schema)
            st = st.where(self.schema.is_completed.isnot(True))
            st = st.where(self.schema.next_action.isnot(None))
            st = st.where(
                self.schema.internal_status.notin_(
                    ORDER_TASK_NOT_TRACKING_STATUSES,
                ),
            )
            st = st.order_by(self.schema.created_at.asc(), self.schema.id.asc())

            result = await session.exec(st)
            return list(result.unique().all())


order_tracking_task_repository = OrderTrackingTaskRepository()
