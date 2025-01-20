from sqlmodel import Session

from infra.database import engine
from scheme.mapping.result.mapping_result_scheme import MappingResult, MappingResultUpdate


def create_mapping_results_list(mapping_results: list[MappingResult]):
    with Session(engine) as session:
        session.add_all(mapping_results)
        session.commit()

        # Update results in list
        for result in mapping_results:
            session.refresh(result)

        return mapping_results


def save_correct_nomenclature(nomenclature: MappingResultUpdate, session: Session) -> MappingResult:
    mapping_result = get_mapping_result_by_id(nomenclature.id, session)
    mapping_result.mapping_nomenclature_corrected = nomenclature.mapping_nomenclature_corrected
    session.merge(mapping_result)
    session.commit()
    return mapping_result


def get_mapping_result_by_id(mapping_result_id: int, session) -> MappingResult:
    # TODO: raise exception when mapping_result is None
    mapping_result_by_id = session.get(MappingResult, mapping_result_id)
    return mapping_result_by_id
