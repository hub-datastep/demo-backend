from sqlmodel import SQLModel


class MostRelevantClassLLMResponse(SQLModel):
    order_class: str
    comment: str


class RulesWithParams(SQLModel):
    rules: list[str]
    exclusion_rules: list[str] | None = None
    is_use_classification: bool | None = None
    is_use_order_updating: bool | None = None


class OrderClassificationLLMResponse(SQLModel):
    most_relevant_class_response: MostRelevantClassLLMResponse
    scores: str
    query_summary: str
