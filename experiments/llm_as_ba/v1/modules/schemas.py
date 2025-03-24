from typing import List, Optional
from sqlmodel import SQLModel
from pydantic import BaseModel, Field


class ResidentRequest(SQLModel):
    """Model representing a resident's request data."""
    request_id: str
    request_content: str
    chat_history: Optional[List[str]] = None
    

class Intent(SQLModel):
    """Model representing the intent of a resident's request."""
    intent_text: str
    intent_source: str # либо из текста заявки либо из чата


class Scenario(SQLModel):
    """Model representing the scenario for handling a resident's request."""
    scenario_type: str  # "actionless_qa" or "action_required"
    description: str


class AnalysisResponse(BaseModel):
    """Model for the analysis response from the LLM."""
    intent_text: str = Field(description="Интент жителя (намерение, с которым он обратился)")
    intent_source: str = Field(description="Где была формулировка интента: 'содержание_заявки', 'чат', 'оба'")
    scenario_type: str = Field(description="Тип сценария: 'actionless_qa' или 'action_required'")
    scenario_details: str = Field(description="Ответ на вопрос жителя или совершенное оператором/специалистом действие")


class RequestAnalysis(SQLModel):
    """Model representing the analysis of a resident's request."""
    request_id: str
    intent: Intent
    scenario: Scenario


class KnowledgeBaseEntry(SQLModel):
    """Model representing an entry in the knowledge base. Each entry corresponds to a single analyzed request."""
    # Initial request data
    request_id: str
    request_content: str
    service: str
    executor_comment: str
    chat_history: str
    
    # LLM output data
    intent_text: str
    intent_source: str
    scenario_type: str
    scenario_details: str
    

class KnowledgeBase(SQLModel):
    """Model representing the knowledge base of typical problems."""
    entries: List[KnowledgeBaseEntry] = [] 
