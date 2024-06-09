from fastapi import APIRouter, Depends
from fastapi_versioning import version

from model import nomenclature_model, synchronize_nomenclatures_model, \
    retrain_noms_classifier_by_groups_model, noms2embeddings_model
from model.auth_model import get_current_user
from scheme.classifier_scheme import RetrainClassifierUpload
from scheme.nomenclature_scheme import JobIdRead, MappingNomenclaturesUpload, MappingNomenclaturesResultRead, \
    SyncNomenclaturesUpload, SyncNomenclaturesResultRead, CreateAndSaveEmbeddingsUpload, CreateAndSaveEmbeddingsResult
from scheme.user_scheme import UserRead

router = APIRouter()


@router.post("/mapping", response_model=JobIdRead)
@version(1)
def start_nomenclature_mapping(
    *,
    current_user: UserRead = Depends(get_current_user),
    body: MappingNomenclaturesUpload,
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
        db_con_str=body.db_con_str,
        table_name=body.table_name,
    )


@router.get("/mapping/{job_ib}", response_model=list[MappingNomenclaturesResultRead])
@version(1)
def get_nomenclature_mapping_result(
    *,
    current_user: UserRead = Depends(get_current_user),
    job_id: str
):
    """
    Получает результат сопоставления номенклатур по указанному идентификаторы задачи.
    """
    return nomenclature_model.get_all_jobs(job_id)


@router.post("/create_and_save_embeddings", response_model=JobIdRead)
@version(1)
def create_and_save_embeddings(
    *,
    current_user: UserRead = Depends(get_current_user),
    body: CreateAndSaveEmbeddingsUpload,
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
    *,
    current_user: UserRead = Depends(get_current_user),
    job_id: str,
):
    """
    Получает результат создания создания векторов в векторсторе для номенклатур из БД.
    """
    return noms2embeddings_model.get_creating_and_saving_nomenclatures_job_result(job_id)


@router.post("/synchronize", response_model=JobIdRead)
@version(1)
def synchronize_nomenclatures(
    *,
    current_user: UserRead = Depends(get_current_user),
    body: SyncNomenclaturesUpload,
):
    """
    Синхронизирует номенклатуры в БД и векторсторе за указанный период.
    """
    return synchronize_nomenclatures_model.start_synchronizing_nomenclatures(
        nom_db_con_str=body.nom_db_con_str,
        chroma_collection_name=body.chroma_collection_name,
        sync_period=body.sync_period
    )


@router.get("/synchronize/{job_id}")
@version(1)
def synchronize_nomenclatures_result(
    *,
    current_user: UserRead = Depends(get_current_user),
    job_id: str
) -> SyncNomenclaturesResultRead:
    """
    Получает результат синхронизации номенклатур в БД и векторсторе.
    """
    return synchronize_nomenclatures_model.get_sync_nomenclatures_job_result(job_id)


@router.post("/retrain_classifier", deprecated=True)
@version(1)
def retrain_classifier_by_groups(
    *,
    current_user: UserRead = Depends(get_current_user),
    body: RetrainClassifierUpload,
):
    """
    Переобучает классификатор по Группам номенклатур.
    Используется фильтрация актуальная только для номенклатур по Группам.
    """
    return retrain_noms_classifier_by_groups_model.start_classifier_retraining(
        db_con_str=body.db_con_str,
        table_name=body.table_name,
        model_description=body.model_description,
    )
