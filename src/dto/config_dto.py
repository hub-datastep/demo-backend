from pydantic import BaseModel


class DatabasePredictionConfigDto(BaseModel):
    is_sql_description: bool
    is_data_check: bool
    is_alternative_questions: bool
