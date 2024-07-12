from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from model import brand_ner_model, load_ner_model

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
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
