import asyncio

import spacy

from infra.env import DATA_FOLDER_PATH


# Создаем класс, чтобы инкапсулировать self.nlp = None
# При функциональном подходе приходится создавать из nlp глобальную переменную,
# а это может повлечь ошибочки при мультипоточном использовании,
# приходится так делать, чтобы поддерживать асинхронную загрузку модели при старте сервера
class NERModel:
    def __init__(self, model_path):
        self.model_path = model_path
        self.ner_model = None

    async def load_model(self):
        loop = asyncio.get_event_loop()
        try:
            self.ner_model = await loop.run_in_executor(
                None,
                spacy.load,
                self.model_path,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load the NER model: {str(e)}")

    def get_ner_brand(self, text: str) -> str:
        if self.ner_model is None:
            raise ValueError("Model is not loaded.")
        doc = self.ner_model(text)
        try:
            return doc.ents[0].text
        except:
            return "ERRORE"
         

    def get_all_ner_brands(self, items: list[str]) -> list[str]:
        brands = []
        for text in items:
            brands.append(self.get_ner_brand(text))
        return brands


# Путь к модели spaCy
brand_model_path = f"{DATA_FOLDER_PATH}/ner_model"
# Создание экземпляра модели
brand_ner_model = NERModel(brand_model_path)


# Асинхронная функция для загрузки модели
async def load_ner_model():
    await brand_ner_model.load_model()
