from sqlmodel import Session, select

from infra.database import engine
from scheme.mapping.mapping_results_scheme import MappingResult
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
