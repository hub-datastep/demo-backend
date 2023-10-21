from datastep.components import datastep_faiss, datastep_multivector
from dto.datastep_prediction_dto import DatastepPredictionOutDto


def get_prediction(filename, query):
    page, response = datastep_faiss.query(filename, query)
    if "Нет" in str(response):
        print("MULTIVECTOR")
        response = datastep_multivector.query(filename, query)
    return DatastepPredictionOutDto(
        answer=response,
        page=page,
        sql="",
        table="",
        similar_queries=[]
    )


if __name__ == "__main__":
    print(get_prediction("Dog23012023_BI_3D_ispr_prava", "характеристики смесителя?"))
