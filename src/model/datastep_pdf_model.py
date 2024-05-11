from sqlmodel import Session

from datastep.components import datastep_faiss
from repository import file_repository
from scheme.prediction_scheme import DocumentPredictionRead


def get_prediction(session: Session, query: str, file_id: int):
    file = file_repository.get_file_by_id(session, file_id)

    response, page = datastep_faiss.query(file.storage_filename, query)
    # if "нет" in response.lower():
    # response = datastep_multivector.query(file.storage_filename, query)

    return DocumentPredictionRead(
        answer=response,
        page=page,
    )
