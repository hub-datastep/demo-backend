from pandas import read_sql, DataFrame
from sqlalchemy import text
from sqlmodel import Session

from repository.tenant.tenant_repository import get_tenant_by_id
from scheme.user.user_scheme import UserRead


def get_similar_nomenclatures(query: str, current_user: UserRead, session: Session) -> list[str]:
    tenant = get_tenant_by_id(session, current_user.tenant_id)
    tenant_db_uri = tenant.db_uri
    nomenclatures_table_name = current_user.classifier_config.nomenclatures_table_name
    similar_nomenclatures = _fetch_items(tenant_db_uri, nomenclatures_table_name, query)
    return similar_nomenclatures['name']


def _fetch_items(db_con_str: str, table_name: str, query: str) -> DataFrame:
    st = text(f"""
        SELECT "name"
        FROM {table_name}
        WHERE "name" ILIKE '%{query}%'
        LIMIT 10
    """)

    return read_sql(st, db_con_str)
