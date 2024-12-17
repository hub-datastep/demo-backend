import uuid

from pandas import read_sql, DataFrame
from sqlalchemy import text
from sqlmodel import Session

from repository.mapping.mapping_result_repository import save_mapping_results_list
from repository.tenant.tenant_repository import get_tenant_by_id
from scheme.mapping.mapping_results_scheme import MappingResult
from scheme.mapping.mapping_scheme import MappingOneNomenclatureRead
from scheme.user.user_scheme import UserRead


def get_similar_nomenclatures(query: str, current_user: UserRead, session: Session) -> list[str]:
    tenant = get_tenant_by_id(session, current_user.tenant_id)
    tenant_db_uri = tenant.db_uri
    nomenclatures_table_name = current_user.classifier_config.nomenclatures_table_name
    similar_nomenclatures = _fetch_items(tenant_db_uri, nomenclatures_table_name, query)
    similar_nomenclatures_list = similar_nomenclatures['name'].to_list()
    return similar_nomenclatures_list


def _fetch_items(db_con_str: str, table_name: str, query: str) -> DataFrame:
    st = text(f"""
        SELECT "name"
        FROM {table_name}
        WHERE "name" ILIKE '%{query}%' AND "is_group" = FALSE
        LIMIT 10
    """)

    return read_sql(st, db_con_str)


def save_mapping_result(
    nomenclatures: list[MappingOneNomenclatureRead],
    user_id: int,
    iteration_key: str,
):
    mapping_results = []
    for nomenclature in nomenclatures:
        mapping_result_dict = nomenclature.dict()
        mapping_result = MappingResult(
            user_id=user_id,
            mapping_result=mapping_result_dict,
            iteration_key=iteration_key,
        )
        mapping_results.append(mapping_result)

    return save_mapping_results_list(mapping_results)


def generate_iteration_key() -> str:
    return str(uuid.uuid4())
