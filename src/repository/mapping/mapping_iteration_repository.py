from sqlalchemy.orm import joinedload
from sqlmodel import select

from infra.database import get_session
from scheme.mapping.result.mapping_iteration_scheme import MappingIteration


def get_iteration_by_id(
    iteration_id: str,
    with_results: bool | None = False,
) -> MappingIteration | None:
    with get_session() as session:
        st = select(MappingIteration)
        st = st.where(MappingIteration.id == iteration_id)

        if with_results:
            st = st.options(
                joinedload(MappingIteration.results),
            )

        iteration = session.exec(st).first()
        return iteration


def create_iteration(iteration: MappingIteration) -> MappingIteration:
    with get_session() as session:
        session.add(iteration)
        session.commit()
        session.refresh(iteration)
        return iteration
