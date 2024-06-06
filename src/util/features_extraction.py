import re

from pandas import DataFrame

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
    "flow_volume": r"(\d+,\d+|\d+) - (\d+,\d+|\d+) л/час",
    # Мощность
    "power": r"(\d+,\d+|\d+)\s?(Вт|кВт)",
    # Вид арматуры
    "reinforcement_type": r"[АAаa]\d+[СCсc]?(?:\(([АAаa1])\))?",
    # Диаметр арматуры
    "reinforcement_diameter": r"No\s?(\d+)|(\d+)мм",
    # Характеристика перемычек
    "jumpers_params": r"(\d+П[ФБ]\d+-\d+)",
    # Диаметр перемычек
    "jumpers_diameter": r"Д(\d+)",
    # Плиты перекрытия
    "floor_slabs": r"П[КБ]\s?\d{2}(?:[.,]?\d+)?(?:-\d+){1,2}",
    # Опорная плита
    "base_plate": r"П\s\d[.,]\d",
    # Типы радиаторов и подключение
    "radiator_types": r"(FK0|FTV)(?: - с (боковым|нижним) подключением)?",
    # Плотность материала
    "density": r"(\d+)кг/м3",
}


def extract_match(pattern: str, text: str) -> str:
    # Extract param by pattern
    match = re.search(pattern, text)
    # Get param as str
    result = str(match.group()) if match else ""
    # Replace special symbols to spaces
    result = re.sub(r"\W+", " ", result)
    return result


def extract_features(nomenclatures: DataFrame) -> DataFrame:
    # Применяем регулярные выражения для извлечения характеристик
    for name, pattern in FEATURES_REGEX_PATTERNS.items():
        nomenclatures[name] = nomenclatures['name'].apply(lambda x: extract_match(pattern, x))

    return nomenclatures


def get_noms_metadatas_with_features(df_noms_with_features: DataFrame) -> list[dict]:
    metadatas = []

    # Разделяем сложную строку на несколько шагов
    for _, row in df_noms_with_features.iterrows():
        # Извлечение значений регулярных выражений
        regex_values = row[FEATURES_REGEX_PATTERNS.keys()].to_dict()

        metadatas.append(regex_values)

    return metadatas
