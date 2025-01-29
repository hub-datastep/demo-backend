from sqlmodel import Session

from infra.database import engine
from scheme.mapping.result.mapping_result_scheme import MappingResult


def get_result_by_id(
    session: Session,
    result_id: int,
) -> MappingResult | None:
    mapping_result = session.get(MappingResult, result_id)
    return mapping_result


def create_mapping_results_list(mapping_results: list[MappingResult]):
    with Session(engine) as session:
        session.add_all(mapping_results)
        session.commit()

        # Update results in list
        for result in mapping_results:
            session.refresh(result)

        return mapping_results


def update_result(
    session: Session,
    mapping_result: MappingResult,
) -> MappingResult:
    session.merge(mapping_result)
    session.commit()
    return mapping_result
