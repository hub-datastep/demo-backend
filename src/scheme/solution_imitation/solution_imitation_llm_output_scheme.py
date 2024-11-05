from sqlmodel import SQLModel, Field


class LLMOutputTable(SQLModel):
    id: str = Field(
        default="",
        description="ID входного элемента",
    )
    input_item: str = Field(
        default="",
        description="Сам входной элемент",
    )
    output_item: str = Field(
        default="",
        description="Выходной элемент",
    )
    additional_info: str = Field(
        default="",
        description="Дополнительная информация по решению или комментарии",
    )


class LLMOutput(SQLModel):
    table: list[LLMOutputTable] = [LLMOutputTable()]
