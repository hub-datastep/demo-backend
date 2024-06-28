import spacy
import os
import asyncio

# Путь к папке data
DATA_FOLDER_PATH = os.path.join(os.path.dirname(__file__), '../../data')

# Путь к модели spaCy
model_path = os.path.join(DATA_FOLDER_PATH, 'ner_model')

# создаем класс чтобы инкапсулировать self.nlp = None
# При функциональном подходе приходится создавать из npl глобальнгую переменную
# а это может повлечь ошибочки при мультипоточном исппользовании
# приходится так делать, тчобы поддерживать асинхронную загрузку модели при старте сервера
class NERModel:
    def __init__(self, model_path):
        self.model_path = model_path
        self.ner_model = None

    async def load_model(self):
        loop = asyncio.get_event_loop()
        try:
            self.ner_model = await loop.run_in_executor(None, spacy.load, model_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load the NER model: {str(e)}")

    def get_ner_brand(self, text: str) -> list[str]:
        if self.ner_model is None:
            raise ValueError("Model is not loaded.")
        doc = self.ner_model(text)
        brands = [ent.text for ent in doc.ents]
        return brands

# Создание экземпляра модели
ner_model_instance = NERModel(model_path)

# Асинхронная функция для загрузки модели
async def load_ner_model():
    await ner_model_instance.load_model()
