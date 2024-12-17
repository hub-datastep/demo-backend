from sqlmodel import Session, select

from infra.database import engine
from scheme.mapping.mapping_results_scheme import MappingResult, MappingResultUpdate


def save_mapping_results_list(mapping_results: list[MappingResult]):
    with Session(engine) as session:
        session.add_all(mapping_results)
        session.commit()


def get_nomenclature_results(session: Session, user_id: int) -> list[MappingResult]:
    statement = select(MappingResult).where(MappingResult.user_id == user_id)
    result = session.exec(statement)
    return list(result.all())


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
