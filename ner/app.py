from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from model import brand_ner_model, load_ner_model
import os

HOST_NER = os.getenv('HOST_NER')

app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})

class TextItems(BaseModel):
    items: List[str]

@app.on_event("startup")
async def startup_event():
    await load_ner_model()

@app.post("/get_brands/")
async def get_brands(text_items: TextItems):
    try:
        brands = brand_ner_model.get_all_ner_brands(text_items.items)
        return {"brands": brands}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=HOST_NER, port=8000, reload=True)