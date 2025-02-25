from sqlmodel import SQLModel


class UTDMaterial(SQLModel):
    row_number: int
    nomenclature: str
    group: str


class LLMMappingKnowledgeBaseCase(SQLModel):
    input_material: str
    predicted_nomenclature: str | None = None
    is_correct: bool | None = None
    feedback: str | None = None
    correct_nomenclature: str


class LLMMappingResponse(SQLModel):
    nomenclature: str | None
    comment: str | None


class LLMMappingResult(SQLModel):
    # Полный ответ LLM
    full_response: dict | None = None
    # Комментарий LLM
    llm_comment: str | None = None
    # Выбранная НСИ номенклатура
    nomenclature: str | None = None
    # Список похожих НСИ номенклатур
    nsi_nomenclatures_list: list[str]
    # Список похожих кейсов из Базы Знаний
    knowledge_base_cases_list: list[dict]
