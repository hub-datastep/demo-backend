import pandas as pd
import re
from util.normalize_name import normalize_name
from util.feature_extraction_regex import regex_patterns


def extract_match(pattern, text):
    match = re.search(pattern, text)
    return match.group() if match else ''

def extract_features(nomenclatures: pd.DataFrame) -> pd.DataFrame:
    # Нормализуем названия номенклатур
    nomenclatures['normalized'] = nomenclatures['nomenclature'].apply(normalize_name)
    
    # Применяем регулярные выражения для извлечения характеристик
    for name, pattern in regex_patterns.items():
        nomenclatures[name] = nomenclatures['nomenclature'].apply(lambda x: extract_match(pattern, x))
    
    return nomenclatures
