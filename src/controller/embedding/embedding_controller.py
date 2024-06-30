from fastapi import APIRouter, Depends
from fastapi_versioning import version

from model.auth.auth_model import get_current_user
from model.embedding import noms2embeddings_model
from scheme.embedding.embedding_scheme import CreateAndSaveEmbeddingsUpload, CreateAndSaveEmbeddingsResult
from scheme.task.task_scheme import JobIdRead
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.post("", response_model=JobIdRead)
@version(1)
def create_and_save_embeddings(
    body: CreateAndSaveEmbeddingsUpload,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Создаёт вектора в векторсторе для всех номенклатур из БД.
    """
    return noms2embeddings_model.start_creating_and_saving_nomenclatures(
        db_con_str=body.db_con_str,
        table_name=body.table_name,
        collection_name=body.collection_name,
        chunk_size=body.chunk_size,
    )


@router.get("/{job_id}", response_model=CreateAndSaveEmbeddingsResult)
@version(1)
def create_and_save_embeddings_result(
    job_id: str,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Получает результат создания векторов в векторсторе для номенклатур из БД.
    """
    return noms2embeddings_model.get_creating_and_saving_nomenclatures_job_result(job_id)
