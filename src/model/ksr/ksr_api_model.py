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
    id_okpd = row['id_okpd']
    name_ksr = row['name']
    units_of_measurement = row['units_of_measure']

    features = {col: row[col] for col in ksr_nomenclature.columns
                if notna(row[col]) and col not in ['id_ksr', 'id_okpd', 'name', 'units_of_measure']}

    return {
        "id_ОКПД": id_okpd,
        "id_КСР": id_ksr,
        "Название": name_ksr,
        "Параметры": features,
        "Ед. изм.": units_of_measurement
    }
