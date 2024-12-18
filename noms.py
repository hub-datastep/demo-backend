import pandas as pd
import pymorphy2

def logic_gen(tag):
    return bool(len([1 for i in ["ADJF", "ADJS", "PRTF", "PRTS"] if i in tag]))

def extract_adj(text):
    try:
        morph = pymorphy2.MorphAnalyzer()
        words = text.split()
        adjectives = [word for word in words if logic_gen(morph.parse(word)[0].tag)]
        print(adjectives)
        return adjectives
    except Exception as e:
        print(f"Ошибка при обработке текста: {e}")
        return []

def read_noms_column(file_path):
    try:
        # Читаем Excel-файл с указанием листа MAIN
        df = pd.read_excel(file_path, sheet_name='MAIN')
        
        # Проверяем, есть ли колонка 'NOMs'
        if 'NOMs' not in df.columns:
            raise ValueError("Колонка 'NOMs' отсутствует в листе MAIN.")
        
        # Возвращаем содержимое колонки 'NOMs' как массив
        return df['NOMs'].dropna().tolist()
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return []

# Пример использования
file_path = "Unistroy.xlsx"
noms_array = read_noms_column(file_path)

noms_array = [extract_adj(i.lower()) for i in noms_array]
print(noms_array)