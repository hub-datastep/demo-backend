import spacy
import os
import asyncio

# Путь к папке data
DATA_FOLDER_PATH = os.path.join(os.path.dirname(__file__), '../../data')

# Путь к модели spaCy
model_path = os.path.join(DATA_FOLDER_PATH, 'ner_model')

# Глобальная переменная для хранения модели
nlp = None

# Функция для асинхронной загрузки модели
async def load_model():
    global nlp
    loop = asyncio.get_event_loop()
    nlp = await loop.run_in_executor(None, spacy.load, model_path)

def get_ner_brand(text):
    if nlp is None:
        raise ValueError("Model is not loaded.")
    # Применение модели к тексту
    doc = nlp(text)
    # Извлечение распознанных сущностей
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities
