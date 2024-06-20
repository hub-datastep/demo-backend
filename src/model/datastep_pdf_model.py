from sqlmodel import Session

from datastep.components import datastep_faiss
from datastep.components.datastep_faiss import search_relevant_description
from repository import file_repository
from repository.file_repository import get_all_filenames_by_tenant_id
from scheme.prediction_scheme import DocumentPredictionRead, DocumentEmptyPredictionRead, KnowledgeBasePredictionRead


def get_prediction(session: Session, query: str, file_id: int):
    file = file_repository.get_file_by_id(session, file_id)

    response, page = datastep_faiss.doc_query(file.storage_filename, query)
    # if "нет" in response.lower():
    # response = datastep_multivector.query(file.storage_filename, query)

    return DocumentPredictionRead(
        answer=response,
        page=page,
    )


def get_prediction_with_relevant_file(session: Session, query: str, tenant_id: int):
    files = get_all_filenames_by_tenant_id(session, tenant_id)
    file_descriptions = [{"filename": file.storage_filename, "description": file.description} for file in files]

    relevant_filename = search_relevant_description(file_descriptions, query)

    if not relevant_filename:
        # Если релевантное описание не найдено
        return DocumentEmptyPredictionRead(
            answer="На основе представленной информации невозможно ответить.",
            # page=None,
            filename=None
        )

    response = datastep_faiss.knowledge_base_query(relevant_filename, query)
    # if "нет" in response.lower():
    # response = datastep_multivector.query(file.storage_filename, query)

    return KnowledgeBasePredictionRead(
        answer=response,
        # page=page,
        filename=relevant_filename
    )
