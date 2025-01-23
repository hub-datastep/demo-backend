from fastapi import HTTPException, status
from pandas import read_sql, DataFrame
from sqlalchemy import text
from sqlmodel import Session

from model.mapping.result import mapping_iteration_model
from model.tenant import tenant_model
from repository.mapping import mapping_iteration_repository, mapping_result_repository
from scheme.mapping.mapping_scheme import MappingOneNomenclatureRead
from scheme.mapping.result.mapping_iteration_scheme import MappingIteration
from scheme.mapping.result.mapping_result_scheme import MappingResult, MappingResultUpdate
from scheme.mapping.result.similar_nomenclature_search_scheme import (
    SimilarNomenclatureSearch,
    SimilarNomenclature,
)
from scheme.user.user_scheme import UserRead


def get_by_id(
    session: Session,
    result_id: int,
) -> MappingResult:
    mapping_result = mapping_result_repository.get_result_by_id(
        session=session,
        result_id=result_id,
    )

    if not mapping_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mapping Result with ID {result_id} not found"
        )

    return mapping_result


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

    return mapping_result_repository.create_mapping_results_list(mapping_results=results_list)


def update_mapping_results_list(
    session: Session,
    body: MappingResultUpdate,
) -> list[MappingResult]:
    # Check if Mapping Iteration exists
    iteration_id = body.iteration_id
    mapping_iteration_model.get_iteration_by_id(
        iteration_id=iteration_id,
    )

    corrected_results_list: list[MappingResult] = []
    for corrected_result in body.corrected_results_list:
        result_id = corrected_result.result_id
        mapping_result = get_by_id(
            session=session,
            result_id=result_id,
        )
        mapping_result.corrected_nomenclature = corrected_result.nomenclature
        update_result = mapping_result_repository.update_result(
            session=session,
            mapping_result=mapping_result,
        )
        corrected_results_list.append(update_result)

    return corrected_results_list
