import asyncio
import spacy
import os

DATA_FOLDER_PATH = os.getenv('DATA_FOLDER_PATH')

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
            print('NER loaded')
        except Exception as e:
            raise RuntimeError(f"Failed to load the NER model: {str(e)}")

    def get_ner_brand(self, text: str) -> str:
        if self.ner_model is None:
            raise ValueError("Model is not loaded.")
        doc = self.ner_model(text).ents
        if doc:
            return doc[0].text
        else:
            return ""
        
    def get_all_ner_brands(self, items: list[str]) -> list[str]:
        if self.ner_model is None:
            raise ValueError("Model is not loaded.")
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
