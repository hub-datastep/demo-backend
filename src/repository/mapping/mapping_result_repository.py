import json
from datetime import datetime

from sqlmodel import Session

from infra.database import engine
from scheme.mapping.mapping_results_scheme import MappingResult
from scheme.mapping.mapping_scheme import MappingOneNomenclatureRead


def save_mapping_nomenclature_result_to_db(nomenclatures: list[MappingOneNomenclatureRead], user_id: int):
    with Session(engine) as session:
        for nomenclature in nomenclatures:
            mapping_result_dict = nomenclature.dict()
            mapping_result = MappingResult(
                user_id=user_id,
                mapping_result=mapping_result_dict,
            )
            session.add(mapping_result)
        session.commit()
        session.refresh(mapping_result)
