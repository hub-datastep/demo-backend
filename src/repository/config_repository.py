from dto.config_dto import DatabasePredictionConfigDto
# from infra.supabase import supabase


def get_database_prediction_config(user_id: str) -> DatabasePredictionConfigDto | None:
    pass
    # response = supabase\
    #     .table("database_prediction_config")\
    #     .select("is_sql_description", "is_data_check", "is_alternative_questions")\
    #     .eq("user_id", user_id)\
    #     .execute()
    #
    # if len(response.data) == 0:
    #     return None
    #
    # return DatabasePredictionConfigDto(**response.data[0])


def update_database_prediction_config(user_id: str, update: DatabasePredictionConfigDto) -> DatabasePredictionConfigDto:
    pass
    # response = supabase \
    #     .table("database_prediction_config") \
    #     .update(update.model_dump()) \
    #     .eq("user_id", user_id) \
    #     .execute()
    #
    # return DatabasePredictionConfigDto(**response.data[0])
