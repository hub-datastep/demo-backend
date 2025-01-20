from fastapi import HTTPException
from pandas import read_sql, DataFrame
from sqlalchemy import text
from sqlmodel import Session

from model.mapping.result import mapping_iteration_model
from repository.mapping import mapping_iteration_repository
from repository.mapping.mapping_result_repository import (
    create_mapping_results_list,
)
from repository.tenant.tenant_repository import get_tenant_by_id
from scheme.mapping.mapping_scheme import MappingOneNomenclatureRead
from scheme.mapping.result.mapping_iteration_scheme import MappingIteration
from scheme.mapping.result.mapping_result_scheme import MappingResult
from scheme.user.user_scheme import UserRead


def get_similar_nomenclatures(query: str, current_user: UserRead, session: Session) -> list[str]:
    tenant = get_tenant_by_id(session, current_user.tenant_id)
    tenant_db_uri = tenant.db_uri
    nomenclatures_table_name = current_user.classifier_config.nomenclatures_table_name
    similar_nomenclatures = _fetch_items(tenant_db_uri, nomenclatures_table_name, query)
    similar_nomenclatures_list = similar_nomenclatures['name'].to_list()
    return similar_nomenclatures_list


def _fetch_items(db_con_str: str, table_name: str, query: str) -> DataFrame:
    st = text(
        f"""
        SELECT "name"
        FROM {table_name}
        WHERE "name" ILIKE '%{query}%' AND "is_group" = FALSE
        LIMIT 10
        """
    )

    return read_sql(st, db_con_str)


def save_mapping_results(
    mappings_list: list[MappingOneNomenclatureRead],
    user_id: int,
    iteration_id: str,
):
    # Check if iteration with this ID exists
    try:
        mapping_iteration_model.get_iteration_by_id(iteration_id=iteration_id)
    except HTTPException:
        # Create iteration if not exists to not lose results
        iteration = MappingIteration(id=iteration_id)
        mapping_iteration_repository.create_iteration(iteration=iteration)

    results_list = []
    for mapping in mappings_list:
        mapping_dict = mapping.dict()
        mapping_result = MappingResult(
            iteration_id=iteration_id,
            user_id=user_id,
            result=mapping_dict,
        )
        results_list.append(mapping_result)

    return create_mapping_results_list(mapping_results=results_list)
