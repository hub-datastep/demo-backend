from sqlmodel import Session, select

from infra.database import engine
from model.mapping.mapping_result_model import get_mapping_result_by_id
from scheme.mapping.mapping_results_scheme import MappingResult, MappingResultUpdate
from scheme.mapping.mapping_scheme import MappingOneNomenclatureRead


def save_mapping_nomenclature_result(nomenclatures: list[MappingOneNomenclatureRead], user_id: int):
    with Session(engine) as session:
        for nomenclature in nomenclatures:
            mapping_result_dict = nomenclature.dict()
            mapping_result = MappingResult(
                user_id=user_id,
                mapping_result=mapping_result_dict,
            )
            session.add(mapping_result)
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
