from sqlmodel import Session

from datastep.components import datastep_faiss
from datastep.components.datastep_faiss import search_relevant_description
from repository.file.file_repository import get_file_by_id, get_all_filenames_by_tenant_id
from scheme.file.file_scheme import KnowledgeBaseFile
from scheme.prediction.prediction_scheme import DocumentPredictionRead, KnowledgeBasePredictionRead
from util.files_paths import get_file_storage_path


def get_prediction(session: Session, query: str, file_id: int):
    file = get_file_by_id(session, file_id)

    response, page = datastep_faiss.doc_query(file.storage_filename, query)
    # if "нет" in response.lower():
    # response = datastep_multivector.query(file.storage_filename, query)

    return DocumentPredictionRead(
        answer=response,
        page=page,
    )


def get_prediction_with_relevant_file(session: Session, query: str, tenant_id: int):
    files = get_all_filenames_by_tenant_id(session, tenant_id)

    knowledge_base_files = [
        KnowledgeBaseFile(
            original_filename=file.original_filename,
            file_description=file.description,
            storage_filename=file.storage_filename,
        ) for file in files
    ]

    relevant_file = search_relevant_description(knowledge_base_files, query)

    if not relevant_file:
        # Если релевантное описание не найдено
        return KnowledgeBasePredictionRead(
            answer="Ни один из представленных документов не содержит информации для ответа на вопрос",
        )

    file_path = str(get_file_storage_path(relevant_file.storage_filename))
    response = datastep_faiss.knowledge_base_query(relevant_file.storage_filename, query)
    filename = relevant_file.original_filename
    # if "нет" in response.lower():
    # response = datastep_multivector.query(file.storage_filename, query)

    return KnowledgeBasePredictionRead(
        answer=response,
        # page=page,
        file_path=file_path,
        filename=filename,
    )
