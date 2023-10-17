from datastep.components import datastep_llama
from datastep.datastep_chains import datastep_pdf_chain
from dto.datastep_prediction_dto import DatastepPredictionOutDto


def get_prediction(filename, query):
    # page, response = datastep_pdf_chain.get_prediction(filename, query)
    page, response = datastep_llama.query(filename, query)
    return DatastepPredictionOutDto(
        answer=response,
        page=page,
        sql="",
        table="",
        similar_queries=[]
    )
