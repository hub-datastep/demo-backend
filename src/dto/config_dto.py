from pydantic import BaseModel

class PredictionConfigDto(BaseModel):
    user_id: str
    is_sql_description: bool
    is_data_check: bool
    is_alternative_questions: bool