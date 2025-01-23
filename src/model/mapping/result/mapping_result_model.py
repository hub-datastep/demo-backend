from fastapi import HTTPException
from pandas import read_sql, DataFrame
from sqlalchemy import text
from sqlmodel import Session

from model.mapping.result import mapping_iteration_model
from model.tenant import tenant_model
from repository.mapping import mapping_iteration_repository
from repository.mapping.mapping_result_repository import (
    create_mapping_results_list,
)
from scheme.mapping.mapping_scheme import MappingOneNomenclatureRead
from scheme.mapping.result.correct_nomenclature_search_scheme import (
    SimilarNomenclatureSearch, SimilarNomenclature,
)
from scheme.mapping.result.mapping_iteration_scheme import MappingIteration
from scheme.mapping.result.mapping_result_scheme import MappingResult
from scheme.user.user_scheme import UserRead


def _fetch_similar_noms(
    db_con_str: str,
    table_name: str,
    nomenclature_name: str,
    limit: int | None = 10,
    offset: int | None = 0,
) -> DataFrame:
    st = text(
        f"""
        SELECT "id", "name"
        FROM {table_name}
        WHERE "name" ILIKE :nomenclature_name
        AND "is_group" = FALSE
        LIMIT {limit}
        OFFSET {offset}
        """
    ).bindparams(
        nomenclature_name=f"%{nomenclature_name}%",
    )
    print(f"SQL stmt: {st}")

    return read_sql(st, db_con_str)


def get_similar_nomenclatures(
    session: Session,
    body: SimilarNomenclatureSearch,
    user: UserRead,
) -> list[SimilarNomenclature]:
    tenant = tenant_model.get_tenant_by_id(
        session=session,
        tenant_id=user.tenant_id,
    )
    tenant_db_uri = tenant.db_uri

    nomenclatures_table_name = user.classifier_config.nomenclatures_table_name

    nomenclature_name = body.name
    similar_noms_df = _fetch_similar_noms(
        db_con_str=tenant_db_uri,
        table_name=nomenclatures_table_name,
        nomenclature_name=nomenclature_name,
    )
    similar_noms_list = [
        SimilarNomenclature(**nom)
        for nom in similar_noms_df.to_dict(orient="records")
    ]

    return similar_noms_list


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
