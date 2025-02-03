from sqlalchemy.orm import joinedload
from sqlmodel import Session, desc, select

from infra.database import engine
from scheme.mapping.result.mapping_iteration_scheme import MappingIteration


def get_iterations_list(
    iteration_id: str | None,
) -> list[MappingIteration]:
    with Session(engine) as session:
        st = select(MappingIteration)
        if iteration_id:
            st = st.where(MappingIteration.id.ilike(f"%{iteration_id}%"))

        # Sort by Created At (date)
        st = st.order_by(desc(MappingIteration.created_at))

        iterations_list = session.exec(st).all()

        return iterations_list


def get_iteration_by_id(
    iteration_id: str,
) -> MappingIteration | None:
    with Session(engine) as session:
        st = select(MappingIteration)
        st = st.where(MappingIteration.id == iteration_id)
        st = st.options(
            joinedload(MappingIteration.results),
        )

        iteration = session.exec(st).first()

        return iteration


def create_iteration(iteration: MappingIteration) -> MappingIteration:
    with Session(engine) as session:
        session.add(iteration)
        session.commit()
        session.refresh(iteration)
        return iteration


def update_iteration(iteration: MappingIteration) -> MappingIteration:
    with Session(engine) as session:
        # session.merge(iteration)
        session.add(iteration)
        session.commit()
        session.refresh(iteration)
        return iteration
