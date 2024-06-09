import re

from pandas import DataFrame
from tqdm import tqdm

tqdm.pandas()

ENG_TO_RUS_CHARS = {
    'a': 'а',
    'b': 'в',
    'e': 'е',
    'k': 'к',
    'm': 'м',
    'h': 'н',
    'o': 'о',
    'p': 'р',
    'c': 'с',
    't': 'т',
    'y': 'у',
    'x': 'х',
}

# Определение регулярных выражений для разных категорий
FEATURES_REGEX_PATTERNS = {
    # Общий размер в мм/см/м
    "overall_size_mm_cm_m": r"(\d+)\s?(мм|см|м)",
    # Диаметр условного отверстия
    "nominal_bore_diameter": r"Ду[-\s]?(\d+)|DN[=\s]?(\d+)",
    # Диаметр (в дюймах)
    "diameter_inches": r"(\d+\/\d+\"|\d+\")",
    # Прямоугольные размеры
    "rectangular_dimensions": r"(\d+)([^\w\s]|[xх])(\d+)(([^\w\s]|[xх])(\d+))?",
    # Давление (PN)
    "pressure_PN": r"[PР][Nn](\d+)",
    # Рабочее давление (Ру)
    "working_pressure_Ru": r"Ру\s?(\d+)",
    # Максимальная температура
    "maximum_temperature": r"[ТT][mMмМ][aAаА][xXкК][Сс]?\s*=?\s*(\d+)\s*[°\s]?[гГ]?[рР]?[CcСсoO]?",
    # Объем потока
    "flow_volume": r"(\d+,\d+|\d+)\s?-\s?(\d+,\d+|\d+) л/час",
    # Мощность
    "power": r"(\d+,\d+|\d+)\s?(Вт|кВт)",
    # Вид арматуры
    "reinforcement_type": r"[АAаa]\d+[СCсc]?(?:\(([АAаa1])\))?",
    # Диаметр арматуры
    "reinforcement_diameter": r"(No|№)\s?(\d+)|(\d+)мм",
    # Характеристика перемычек
    "jumpers_params": r"(\d+П[ФБ]\d+-\d+)",
    # Диаметр перемычек
    "jumpers_diameter": r"Д(\d+)",
    # Плиты перекрытия
    "floor_slabs": r"П[КБ]\s?\d{2}(?:[.,]?\d+)?(?:-\d+){1,2}",
    # Опорная плита
    "base_plate": r"П\s\d[.,]\d",
    # Типы радиаторов и подключение
    "radiator_types": r"(FK0|FTV)|(с (боковым|нижним) подключением)",
    # Плотность материала
    "density": r"(\d+)кг/м3",
}


def extract_match(pattern: str, text: str) -> str:
    # Extract param by pattern
    match = re.search(pattern, text, flags=re.IGNORECASE)
    # Get param as str
    result = str(match.group()) if match else ""

    # Replace special symbols to spaces
    result = re.sub(r"[^A-zА-я0-9 ]+|[xх_]+", "-", result)

    # Remove "No", "№", "мм" from reinforcement_diameter param
    # It should contain only number
    if re.match(FEATURES_REGEX_PATTERNS['reinforcement_diameter'], result):
        result = re.sub(r"(No|№)|(мм)", "", result)

    # Change "FK0" to "с боковым подключением" in radiator_types param
    if re.match(r"(FK0)", result):
        result = re.sub(r"(FK0)", "с боковым подключением", result)

    # Change "FTV" to "с нижним подключением" in radiator_types param
    elif re.match(r"(FTV)", result):
        result = re.sub(r"(FTV)", "с нижним подключением", result)

    # Turn to lower case
    result = result.lower()
    # Remove spaces and other at the start and end of string
    result = str(result.strip())

    # Replace eng chars to equal russian
    for en_char, ru_char in ENG_TO_RUS_CHARS.items():
        result = result.replace(en_char, ru_char)

    return result


def extract_features(nomenclatures: DataFrame) -> DataFrame:
    # Применяем регулярные выражения для извлечения характеристик
    for name, pattern in FEATURES_REGEX_PATTERNS.items():
        nomenclatures[name] = nomenclatures['name'].progress_apply(
            lambda nom_name: extract_match(pattern, nom_name)
        )

    return nomenclatures


def get_noms_metadatas_with_features(df_noms_with_features: DataFrame) -> list[dict]:
    metadatas = []

    # Разделяем сложную строку на несколько шагов
    for _, row in df_noms_with_features.iterrows():
        # Извлечение значений регулярных выражений
        # Возвращает объект вида {regex_name: nomenclature_param}
        regex_values = row[FEATURES_REGEX_PATTERNS.keys()].to_dict()

        metadatas.append(regex_values)

    return metadatas
