from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi_versioning import version

from model import nomenclature_model, noms2embeddings_model, synchronize_nomenclatures_model, \
    retrain_noms_classifier_by_groups_model
from model.auth_model import get_current_user
from scheme.classifier_scheme import RetrainClassifierUpload
from scheme.nomenclature_scheme import JobIdRead, MappingNomenclaturesUpload, MappingNomenclaturesResultRead, \
    CreateAndSaveEmbeddingsUpload, \
    SyncNomenclaturesUpload, SyncNomenclaturesResultRead, CreateAndSaveEmbeddingsResult
from scheme.user_scheme import UserRead

router = APIRouter()


@router.get("/{job_id}", response_model=list[MappingNomenclaturesResultRead])
@version(1)
def get_nomenclature_mappings(
    *,
    current_user: UserRead = Depends(get_current_user),
    job_id: str
):
    """
    Получает результат сопоставления номенклатур по указанному идентификаторы задачи.

    Args:
        job_id (str): Идентификатор задачи.

    Returns:
        list[MappingNomenclaturesResultRead]: Список результатов сопоставления.
        - ready_count (int): То, сколько номенклатур уже смаппилось.
        - total_count (int): То, сколько всего номенклатур нужно смаппить.
        - nomenclatures (list): Итоги маппинга
        -- nomenclature (str): Название исходной номенклатуры
        -- group (str): Найденная группа для исходной номенклатуры
        -- mappings (list): Варианты похожих номенклатур
        ---- nomenclature (str): Смаппленная номенклатура
        ---- similarity_score (float): Расстояние между векторами (от 0 до 1).
        Чем меньше значение, тем более похожи номенклатуры (0 - значит они идентичны).
    """
    return nomenclature_model.get_all_jobs(job_id)


@router.post("/mapping", response_model=JobIdRead)
@version(1)
def start_nomenclature_mapping(
    *,
    current_user: UserRead = Depends(get_current_user),
    nomenclatures: MappingNomenclaturesUpload,
    model_id: str,
):
    """
    Запускает процесс сопоставления номенклатур.

    Args:
        nomenclatures (MappingNomenclaturesUpload): Номенклатуры для сопоставления.
        model_id (str): ID модели классификатора.

    Returns:
        JobIdRead: Идентификатор задачи.
    """
    return nomenclature_model.start_mapping(nomenclatures, model_id)


@router.post("/collection/{collection_name}")
@version(1)
def create_chroma_collection(
    *,
    current_user: UserRead = Depends(get_current_user),
    collection_name: str
):
    """
    Создает Chroma коллекцию.

    Args:
        collection_name (str): Название коллекции.
    """
    return noms2embeddings_model.create_chroma_collection(collection_name=collection_name)


@router.get("/collection/{collection_name}/length")
@version(1)
def get_chroma_collection_length(
    *,
    current_user: UserRead = Depends(get_current_user),
    collection_name: str
) -> int:
    """
    Получает количество векторов в Chroma коллекции.

    Args:
        collection_name (str): Название коллекции.

    Returns:
        int: Количество векторов коллекции.
    """
    return noms2embeddings_model.get_chroma_collection_length(collection_name=collection_name)


@router.delete("/collection/{collection_name}")
@version(1)
def delete_chroma_collection(
    *,
    current_user: UserRead = Depends(get_current_user),
    collection_name: str
):
    """
    Удаляет Chroma коллекцию.

    Args:
        collection_name (str): Название коллекции.
    """
    return noms2embeddings_model.delete_chroma_collection(collection_name=collection_name)


@router.post("/collection/create_and_save", response_model=JobIdRead)
@version(1)
def create_and_save_embeddings(
    *,
    current_user: UserRead = Depends(get_current_user),
    background_tasks: BackgroundTasks,
    body: CreateAndSaveEmbeddingsUpload,
):
    job_id = noms2embeddings_model.start_creating_and_saving_nomenclatures(
        db_con_str=body.db_con_str,
        table_name=body.db_con_str,
        collection_name=body.collection_name,
        chunk_size=body.chunk_size,
    )
    return job_id


@router.get("/collection/create_and_save/result", response_model=CreateAndSaveEmbeddingsResult)
@version(1)
def create_and_save_embeddings_result(
    *,
    current_user: UserRead = Depends(get_current_user),
    background_tasks: BackgroundTasks,
    job_id: str,
):
    job_result = noms2embeddings_model.get_creating_and_saving_nomenclatures_job_result(job_id)
    return job_result


@router.post("/synchronize", response_model=JobIdRead)
@version(1)
def synchronize_nomenclatures(
    *,
    body: SyncNomenclaturesUpload,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Синхронизирует номенклатуры в ДВХ МСУ и векторсторе за указанный период.

    Args:
        body (SyncNomenclaturesUpload): Тело запроса.
            - nom_db_con_str (str): Строка подключения к базе данных
            - chroma_collection_name (str): Название Chroma коллекции
            - sync_period (int): Период синхронизации в часах

    Returns:
        JobIdRead: Идентификатор задачи.
    """
    return synchronize_nomenclatures_model.start_synchronizing_nomenclatures(
        nom_db_con_str=body.nom_db_con_str,
        chroma_collection_name=body.chroma_collection_name,
        sync_period=body.sync_period
    )


@router.post("/synchronize/result")
@version(1)
def synchronize_nomenclatures_result(
    *,
    current_user: UserRead = Depends(get_current_user),
    job_id: str
) -> SyncNomenclaturesResultRead:
    """
    Получает результат синхронизации номенклатур в ДВХ МСУ и векторсторе.

    Args:
        job_id (str): Идентификатор задачи.

    Returns:
        SyncNomenclaturesResultRead: Результат синхронизации номенклатур.
    """
    return synchronize_nomenclatures_model.get_sync_nomenclatures_job_result(job_id)


@router.post("/retrain_classifier")
@version(1)
def retrain_classifier_by_groups(
    *,
    body: RetrainClassifierUpload,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Переобучает классификатор по Группам номенклатур.
    Используется фильтрация актуальная только для номенклатур по Группам.

    Args:
        body (RetrainClassifierUpload): Тело запроса.
            - db_con_str (str): Строка подключения к базе данных
            - table_name (str): Таблица, по которой классификатор будет обучаться (например: us.СправочникНоменклатура)
            - model_description (str): Описание классификатора (на чём обучен, для чего и т.п.)

    Returns:
        JobIdRead: Идентификатор задачи.
    """
    return retrain_noms_classifier_by_groups_model.start_classifier_retraining(
        db_con_str=body.db_con_str,
        table_name=body.table_name,
        model_description=body.model_description,
    )

# @router.post("/by_views")
# @version(1)
# def retrain_classifier_by_views(
#     *,
#     body: RetrainClassifierUpload,
#     current_user: UserRead = Depends(get_current_user),
# ):
#     return retrain_classifier_by_views_model.start_classifier_retraining(
#         db_con_str=body.db_con_str,
#         table_name=body.table_name,
#     )


# @router.post("/synchronize/by_views", response_model=JobIdRead)
# @version(1)
# def synchronize_nomenclatures_by_views(
#     *,
#     body: SyncNomenclaturesByViewsUpload,
#     current_user: UserRead = Depends(get_current_user),
# ):
#     return synchronize_nomenclatures_by_views_model.start_synchronizing_nomenclatures(
#         db_con_str=body.db_con_str,
#         table_name=body.table_name,
#         chroma_collection_name=body.chroma_collection_name,
#     )
