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
        "SDR_and_dimensions": r"(?i)\bSDR(\d+(?:[\.,]\d+)?)(?:\s*-\s*)?(\d+(?:[\.,]\d+))\s*[xх]\s*(\d+(?:[\.,]\d+))\b",

        # Pipe length in meters: matches "number" + "m" (case-insensitive),
        # allows spaces before "m". Examples: "12m", " 12M", "(12m)", etc.
        "length_in_meters": r"(?i)\b(\d+(?:[\.,]\d+)?)\s*[мm]\b",
    }
}




import re
import pandas as pd

def get_noms_metadatas_with_features(
    df_noms_with_features: pd.DataFrame,
    features_regex_patterns_for_class: dict
) -> list[dict]:
    """
    Функция формирует метаданные (результаты регулярных выражений) по каждой строке df_noms_with_features.
    
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
        
    :return: список словарей вида:
        [
          {
            "NOMs": <str>,
            "features": {
              <имя_свойства_1>: <строка_совпадения_или_None>,
              <имя_свойства_2>: <строка_совпадения_или_None>,
              ...
            }
          },
          ...
        ]
    """
    results = []

    for _, row in df_noms_with_features.iterrows():
        nom = row["NOMs"]
        group_name = row["GROUP"]

        # Получаем набор регулярных выражений для текущей группы
        group_patterns = features_regex_patterns_for_class.get(group_name, {})

        # Применяем регулярки к NOM
        features_dict = {}
        for feature_name, pattern in group_patterns.items():
            match = re.search(pattern, str(nom))
            if match:
                # Сохраняем всё совпадение (group(0)), 
                # либо, при необходимости, какую-то определённую группу: match.group(1)
                features_dict[feature_name] = match.group(0)
            else:
                features_dict[feature_name] = None
        
        # Формируем итоговую запись
        # result_item = features_dict if features_dict else None
        # results.append(result_item)
        if features_dict:
            results.append(features_dict)
    
    return results


def main():
    # Считываем Excel (лишь колонки NOMs и GROUP)
    df_sample = pd.read_excel(
        r"E:\Unistroy.xlsx",
        sheet_name='MAIN',
        usecols=['NOMs', 'GROUP']
    )
    #  data = {
    #     "NOMs": [
    #         "Бетон М-100",
    #         "Бетон М-100 (- 5С)",
    #         "Бетон М-150",
    #         "Бетон М150 (- 5С)",
    #         "ЩЭ 4 квартиры",
    #         "Щит этажный (пробный первый вариант)"
    #     ],
    #     "GROUP": [
    #         "Бетон Материалы",
    #         "Бетон Материалы",
    #         "Бетон Материалы",
    #         "Бетон Материалы",
    #         "Щитовое оборудование Материалы",
    #         "Щитовое оборудование Материалы"
    #     ]
    # }

    # df_sample = pd.DataFrame(data)

    result = get_noms_metadatas_with_features(df_sample, FEATURES_REGEX_PATTERNS_FOR_CLASS)
    for item in result:
        print(item)

if __name__ == "__main__":
    main()
