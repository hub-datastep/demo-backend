import re

from pandas import DataFrame, concat, ExcelWriter
from tqdm import tqdm
import numpy as np

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


FEATURES_REGEX_PATTERNS_FOR_CLASS = {
    "Бетон Материалы": {

        # 1) "М-100" и "М150", включая варианты с латиницей/транслитом:
        #    Класс [MmМм] — любые из (M, m, М, м).
        #    - (дефис) опционален
        #    - число 3 цифры, кратное 10 (100..800)
        "mark_strength": r"\b[MmМм]-?(?:[1-7]\d|80)0\b",

        # 2) Температура (в скобках), может быть `+` или `-` или без знака, 
        #    C/С (лат/кир) в любом регистре, символ градуса опционален:
        "temperature": (
            r"\(\s*[+\-]?\s*\d+\s*"
            r"[CcСс]"   # C или С (любой регистр)
            r"(?:°)?\)" # символ градуса опционален
        ),

        # 3) "W4", "w6" и т.д.: (W/w + чётное число)
        #    Если хотим ещё учесть, что кто-то мог написать "ш" (очень сомнительный кейс),
        #    тогда расширяем класс до [WwШш] и проверяем, нужно ли это реально:
        "w_even": r"\b[Ww]\d*[02468]\b",

        # 4) "F100" / "f500" и т.д. (диапазон 50..1000)
        #    Аналогично, если транслит "f" -> "ф", то можно дописать в класс [FfФф], 
        #    но только если точно знаем, что в данных бывает именно такой неверный ввод:
        "f_range": r"\b[Ff](?:[5-9]\d|[1-9]\d{2}|1000)\b",

        # 5) "АБН-24м" (АБН в разных регистрах, тире, число, в конце «м»):
        #    - Если люди могут писать латиницу "ABH", которая на вид похожа на "АБН", 
        #      придётся дописывать класс: [Aa][Bb][Hh] и т.д.
        #      Но здесь покажем только кириллицу в любом регистре:
        "abn": r"\b[Аа][Бб][Нн]-\d+[мМ]\b",

        # 6) "B8"/"b7,5": (B/b + число (целое или дробное через запятую)).
        #    - Если бывает путаница "b" -> "в" (по транслиту 'b' => 'в'), 
        #      и нам нужно ловить именно "B" (как бетонный класс "B25" -> "В25"?),
        #      то можно расширить класс, напр.: [BbВв].
        "class_strength": r"\b[Bb]\d+(?:,\d+)?\b",
    },
    "Водоснабжение и Канализация":{
        # SN (stiffness class) — matches 'SN' (case-insensitive) + 1-2 digits
        # Handles variations with or without spaces: "SN10", "sn 8", "Sn   16", etc.
        "stiffness_class_SN": r"(?i)\bSN\s*(\d{1,2})\b",

        # ID (internal diameter) — matches 'ID' (case-insensitive) + 2-3 digits,
        # optionally followed by "/..." including variations like "DN" before numbers.
        # Examples: "ID200", "ID300/345", "ID200/DN225", etc.
        "internal_diameter_ID": r"(?i)\bID\s*(\d{2,3})(?:\s*/\s*(?:DN\s*)?\d{1,4})?\b",

        # OD (external diameter) — similar to ID but for 'OD'.
        # Examples: "OD315", "OD400/345", "OD250/217", "OD200/DN225", etc.
        "external_diameter_OD": r"(?i)\bOD\s*(\d{2,3})(?:\s*/\s*(?:DN\s*)?\d{1,4})?\b",

        # Dimensions in the form "number x number" (handles both Cyrillic and Latin 'x')
        # Example: "3600х6980", "200x18,2" (if not preceded by SDR)
        "dimensions_length_width": r"(?i)\b(\d+(?:[\.,]\d+)?)\s*[xх]\s*(\d+(?:[\.,]\d+)?)\b",

        # SDR + dimensions: "SDR11 - 200х18,2", where:
        # - "SDR" may or may not have spaces around it, may have a decimal part (e.g., SDR17.6)
        # - after SDR and optional dash, there are two groups "number x number",
        #   each group can have a decimal part.
        # Example: "SDR11 - 200х18,2", "SDR17.6-280х16,6", etc.
        "SDR_and_dimensions": r"(?i)\bSDR\s*(\d{1,2})\b",

        # Pipe length in meters: matches "number" + "m" (case-insensitive),
        # allows spaces before "m". Examples: "12m", " 12M", "(12m)", etc.
        "length_in_meters": r"(?i)\b(\d+(?:[\.,]\d+)?)\s*[мm]\b",

        "pe": r"\b[Пп][ЭЕEe][\s-]?(\d{2,4})\b"
    },
    "Лифтовое оборудование Материалы":{
        "payload": r"(?i)\b(?:г/п\s*[:\-]?\s*(\d+)\s*кг|(\d+)\s*кг)\b",
        "number_of_stops": r"(?i)\b(\d+)\s*ост(?:\.|ановок)?\b",
        "speed": r"(?i)\b(\d+(?:\.\d+)?)\s*м/с\b",
        "machine_room": r"(?i)\b(?:Без\s*МП|С\s*МП)\b",
        "usage_type": r"(?i)\b(?:пассажирский|грузовой)\b",

    },
    "Блоки и другие стеновые материалы": {
        "dimensions": r"(?i)\b(\d{2,4}[xх]\d{2,4}[xх]\d{2,4})\b",  # Matches dimensions like 390x190x188
        "strength_class": r"(?i)\b([Mм][-\s]?\d{2,3})\b",  # Matches M75, M-75, M 75
        "standard": r"(?i)\b(ГОСТ\s?\d{4,5}-\d{4})\b",  # Matches standards like ГОСТ 33126-2014
    },
    "Пазогребневые плиты гипсовые Материалы": {
        "dimensions": r"(?i)\b\d{3}[х*]\d{3}[х*]\d{2,3}(мм)?\b"

    },
    "Перемычки железобетонные Материалы": {
        # Matches sizes with "пб" (e.g., "10 пб", "10пб") and "пп" (e.g., "10 пп", "10пп")
        "size_p": r"(?i)\b(\d{1,2})\s*п[бп]\b",

        # Matches range values, optionally followed by "п" (e.g., "21-27", "21-27 п")
        "range": r"\b(\d{1,2})\s*-\s*(\d{1,2})",
    },
    "Плиты перекрытия железобетонные пустотные Материалы": {
        "material_type": r"(?i)\bП[БК]\b",
        "dimensions": r"\b\d{1,3}-\d{1,3}-\d{1,3}т?(?:,\d{1,2})?(?=\s|[AА]тVт|\()",
        "additional_info": r"(?i)[AА]тVт",
        "weight": r"\d+,\d{1,2}"
    }
}


def extract_match(pattern: str, text: str) -> str:
    # Extract param by pattern
    match = re.search(pattern, text, flags=re.IGNORECASE)
    # Get param as str
    result = str(match.group()) if match else ""

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

    # Replace special symbols to spaces
    result = re.sub(r"[^A-zА-я0-9 ]+|[xх_]+", "-", result)

    # Turn to lower case
    result = result.lower()
    # Remove spaces and other at the start and end of string
    result = str(result.strip())

    # Replace eng chars to equal russian
    for en_char, ru_char in ENG_TO_RUS_CHARS.items():
        result = result.replace(en_char, ru_char)

    return result

def get_noms_metadatas_with_features(
    df_noms_with_features: DataFrame,
    noms_name: str = "name",
    noms_group: str = "internal_group",
    features_regex_patterns_for_class: dict = FEATURES_REGEX_PATTERNS_FOR_CLASS
) -> DataFrame:
    """
    Функция формирует метаданные (результаты регулярных выражений) по каждой строке df_noms_with_features и добавляет их в новый DataFrame.
    
    :param df_noms_with_features: DataFrame с колонками [NOMs, GROUP] (минимально необходимые).
    :param features_regex_patterns_for_class: словарь вида:
        {
          "Бетон Материалы": {
              "прочность": r"(M|М)-?\d+",
              "температура": r"\(-\s?\d+С\)"
              # и т.д.
          },
          "Щитовое оборудование Материалы": {
              "тип_щита": r"Щ[ОСЭ].*",
              "этажность": r"\d+\s?квартир"
              # и т.д.
          },
          ...
        }
        
    :return: DataFrame с добавленными столбцами для каждого свойства
    """
    expanded_df = df_noms_with_features.copy()  # Копируем исходный DataFrame для модификации
    
    for _, row in df_noms_with_features.iterrows():
        nom = row[noms_name]
        group_name = row[noms_group]

        # Получаем набор регулярных выражений для текущей группы
        group_patterns = features_regex_patterns_for_class.get(group_name, {})

        # Применяем регулярки к NOM и добавляем в новые столбцы
        for feature_name, pattern in group_patterns.items():
            match = re.search(pattern, str(nom))
            if match:
                # Если есть совпадение, сохраняем его
                expanded_df.at[_, feature_name] = match.group(0).lower()
            else:
                # Если совпадения нет, присваиваем NaN
                expanded_df.at[_, feature_name] = np.nan

    return expanded_df


# TODO смотреть здесь
def get_noms_metadatas_with_features(df_noms_with_features: DataFrame) -> list[dict]:
    metadatas = []

    # Разделяем сложную строку на несколько шагов
    for _, row in df_noms_with_features.iterrows():
        # Извлечение значений регулярных выражений
        # Возвращает объект вида {regex_name: nomenclature_param}
        regex_values = row[FEATURES_REGEX_PATTERNS.keys()].to_dict()

        # regex_values.update({
        #     "brand": row['brand']
        # })

        metadatas.append(regex_values)

    return metadatas

if __name__=="__main__":
    # Пример тестового набора данных
    data = {
        "internal_group": ["Бетон Материалы", "Водоснабжение и Канализация", "Лифтовое оборудование Материалы"],
        "name": [
            "М-100 (температура +20С) W4 F500 АБН-24м B7,5",  # Пример с разными признаками из группы "Бетон Материалы"
            "SN10 ID200 OD315 3600х6980 SDR11 - 200х18,2",  # Пример из группы "Водоснабжение и Канализация"
            "г/п 500кг 3 остановки 1,5м/с Без МП",  # Пример из группы "Лифтовое оборудование Материалы"
        ]
    }

    # Создаем DataFrame
    nomenclatures = DataFrame(data)

    # Применяем функцию
    extracted_features = extract_features(nomenclatures)

    extracted_features.to_excel('output.xlsx', index=False)  
    # Выводим результат
    print(extracted_features)