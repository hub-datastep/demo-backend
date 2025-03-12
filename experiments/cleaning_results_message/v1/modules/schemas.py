from sqlmodel import SQLModel


class CleaningResultMessageLLMResponse(SQLModel):
    # Коммент исполнителя после фильтрации
    filtered_comment: str | None = None
    # Пояснение LLM как она писала сообщение
    comment: str | None = None
    # Текст сообщения
    message: str | None = None
