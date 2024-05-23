import re

from pandas import DataFrame

from util.normalize_name import normalize_name

# Определение регулярных выражений для разных категорий
FEATURES_REGEX_PATTERNS = {
    # Общий размер в мм/см/м
    "overall_size_mm_cm_m": r"(\d+)\s?(мм|см|м)",
    # Диаметр условного отверстия
    "nominal_bore_diameter": r"Ду-?(\d+)|DN=?(\d+)",
    # Диаметр (в дюймах)
    "diameter_inches": r"(\d+\/\d+\"|\d+\")",
    # Прямоугольные размеры
    "rectangular_dimensions": r"(\d+)[xх](\d+)(?:[xх](\d+))?",
    # Давление (PN)
    "pressure_PN": r"[PР][Nn](\d+)",
    # Рабочее давление (Ру)
    "working_pressure_Ru": r"Ру\s?(\d+)",
    # Максимальная температура
    "maximum_temperature": r"[ТT][mMмМ][aAаА][xXкК][Сс]?\s*=?\s*(\d+)\s*[°\s]?[гГ]?[рР]?[CcСсoO]?",
    # Объем потока
    "flow_volume": r"(\d+,\d+|\d+) - (\d+,\d+|\д+) л/час",
    # Мощность
    "power": r"(\д+)\s?(Вт|кВт)",
}


def extract_match(pattern, text):
    match = re.search(pattern, text)
    return match.group() if match else ''


def extract_features(nomenclatures: DataFrame) -> DataFrame:
    # Нормализуем названия номенклатур
    nomenclatures['normalized'] = nomenclatures['nomenclature'].apply(normalize_name)

    # Применяем регулярные выражения для извлечения характеристик
    for name, pattern in FEATURES_REGEX_PATTERNS.items():
        nomenclatures[name] = nomenclatures['nomenclature'].apply(lambda x: extract_match(pattern, x))

    return nomenclatures
