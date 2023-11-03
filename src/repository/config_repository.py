from dto.config_dto import DatabasePredictionConfigDto
from infra.supabase import supabase


def get_database_prediction_config(user_id: str) -> DatabasePredictionConfigDto | None:
    response = supabase\
        .table("database_prediction_config")\
        .select("is_sql_description", "is_data_check", "is_alternative_questions")\
        .eq("user_id", user_id)\
        .execute()

    if len(response.data) == 0:
        return None

    return DatabasePredictionConfigDto(**response.data[0])
