from pandas import read_sql, notna
from sqlalchemy import text
from infra.env import DB_CONNECTION_STRING


def get_ksr(id_ksr: str) -> dict:
    st = text(f"""
            SELECT *
            FROM autoban_ksr_api.ksr_nomenclatures
            WHERE "id_ksr" = '{id_ksr}'
        """)
    ksr_nomenclature = read_sql(st, DB_CONNECTION_STRING)
    if ksr_nomenclature.empty:
        return {"error": "No data found for the given id_ksr"}

    row = ksr_nomenclature.iloc[0]
    name_ksr = row['name']
    group_id = row['group_id']
    group_name = row['group_name']
    units_of_measurement = row['units_of_measure']

    features = {col: row[col] for col in ksr_nomenclature.columns
                if notna(row[col]) and row[col] != "" and col not in ['id_ksr', 'group_id', 'group_name', 'name', 'units_of_measure']}

    return {
        "id_КСР": id_ksr,
        "group_id": group_id,
        "group_name": group_name,
        "name_ksr": name_ksr,
        "parameters": features,
        "units_of_measurement": units_of_measurement,
    }
