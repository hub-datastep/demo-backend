from fastapi import APIRouter, Depends
from fastapi_versioning import version

from model import nomenclature_model, synchronize_nomenclatures_model, noms2embeddings_model
from model.auth_model import get_current_user
from scheme.nomenclature_scheme import JobIdRead, MappingNomenclaturesUpload, MappingNomenclaturesResultRead, \
    SyncNomenclaturesUpload, SyncNomenclaturesResultRead, CreateAndSaveEmbeddingsUpload, CreateAndSaveEmbeddingsResult
from scheme.user_scheme import UserRead

router = APIRouter()


@router.post("/mapping", response_model=JobIdRead)
@version(1)
def start_nomenclature_mapping(
    body: MappingNomenclaturesUpload,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Запускает процесс сопоставления номенклатур.
    """
    return nomenclature_model.start_mapping(
        nomenclatures=body.nomenclatures,
        most_similar_count=body.most_similar_count,
        chroma_collection_name=body.chroma_collection_name,
        chunk_size=body.chunk_size,
        model_id=body.model_id,
        use_params=body.use_params,
        classifier_config=current_user.classifier_config,
    )


@router.get("/mapping/{job_id}", response_model=list[MappingNomenclaturesResultRead])
@version(1)
def get_nomenclature_mapping_result(
    job_id: str,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Получает результат сопоставления номенклатур через указанный идентификатор задачи.
    """
    return nomenclature_model.get_all_jobs(job_id)


@router.post("/create_and_save_embeddings", response_model=JobIdRead)
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


@router.get("/create_and_save_embeddings/{job_id}", response_model=CreateAndSaveEmbeddingsResult)
@version(1)
def create_and_save_embeddings_result(
    job_id: str,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Получает результат создания векторов в векторсторе для номенклатур из БД.
    """
    return noms2embeddings_model.get_creating_and_saving_nomenclatures_job_result(job_id)


@router.post("/synchronize", response_model=JobIdRead)
@version(1)
def synchronize_nomenclatures(
    body: SyncNomenclaturesUpload,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Синхронизирует номенклатуры в БД и векторсторе за указанный период.
    """
    return synchronize_nomenclatures_model.start_synchronizing_nomenclatures(
        nom_db_con_str=body.nom_db_con_str,
        chroma_collection_name=body.chroma_collection_name,
        sync_period=body.sync_period,
    )


@router.get("/synchronize/{job_id}")
@version(1)
def synchronize_nomenclatures_result(
    job_id: str,
    current_user: UserRead = Depends(get_current_user),
) -> SyncNomenclaturesResultRead:
    """
    Получает результат синхронизации номенклатур в БД и векторсторе.
    """
    return synchronize_nomenclatures_model.get_sync_nomenclatures_job_result(job_id)
