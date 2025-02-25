from sqlmodel import SQLModel

from scheme.mapping.mapping_scheme import MappingOneNomenclatureRead


class LLMMappingKnowledgeBaseCase(SQLModel):
    """
    Схема кейсов из Базы Знаний (истории сопоставлений).
    """

    # Входной материал
    input_material: str
    # Предсказанная НСИ номенклатура
    predicted_nomenclature: str | None = None
    # Правильное или Неправильное сопоставление
    is_correct: bool | None = None
    # Фидбек/Комментарий
    feedback: str | None = None
    # Правильная (ожидаемая) НСИ номенклатура
    correct_nomenclature: str


class LLMMappingResponse(SQLModel):
    """
    Схема ответа от LLM для маппинга.
    """

    # Объяснения LLM почему она выбрала/не выбрала определённый материал
    comment: str | None = None
    # Выбранная НСИ номенклатура
    nomenclature: str | None = None


class LLMMappingResult(MappingOneNomenclatureRead):
    """
    Схема результатов маппинга с LLM. Эти данные сохраняются в БД.
    """

    # Полный ответ LLM
    full_response: dict | None = None
    # Комментарий LLM
    llm_comment: str | None = None
    # Все параметры смапленной номенклатуры из НСИ (таблицы БД)
    nomenclature_data: dict | None = None
    # Список похожих НСИ номенклатур
    nsi_nomenclatures_list: list[str]
    # Список похожих кейсов из Базы Знаний
    knowledge_base_cases_list: list[LLMMappingKnowledgeBaseCase]
