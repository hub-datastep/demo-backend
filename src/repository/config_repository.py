from dto.config_dto import PredictionConfigDto
from infra.supabase import supabase

def get_database_prediction_config(user_id: str) -> PredictionConfigDto:
    (_, [config]), _ =  supabase\
        .table("database_prediction_config")\
        .select("*")\
        .eq("user_id", user_id)\
        .execute()
    return config
