from datastep.components import datastep_faiss, datastep_multivector
from scheme.prediction_scheme import DocumentPredictionRead


def get_prediction(filename, query):
    page, response = datastep_faiss.query(filename, query)
    if "Нет" in str(response):
        response = datastep_multivector.query(filename, query)
    return DocumentPredictionRead(
        answer=response,
        page=page,
    )


if __name__ == "__main__":
    print(get_prediction("Dog23012023_BI_3D_ispr_prava", "характеристики смесителя?"))
