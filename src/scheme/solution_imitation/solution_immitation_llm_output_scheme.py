from pydantic import BaseModel, Field
from typing import List

class LLMOutputTableItem(BaseModel):
    output_string: str = Field("", description="Сам элемент")
    additional_info: str = Field("", description="Дополнительная информация по решению или комментарии")

class LLMOutputTable(BaseModel):
    id: str = Field("", description="ID элемента из входного массива данных")
    output_item: list[LLMOutputTableItem] = Field(default_factory=list, description="Объект для ответа")