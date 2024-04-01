from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi_versioning import version

from model import nomenclature_model, noms2embeddings_model, synchronize_nomenclatures_model
from model.auth_model import get_current_user
from scheme.nomenclature_scheme import JobIdRead, MappingNomenclaturesUpload, MappingNomenclaturesResultRead, \
    CreateAndSaveEmbeddingsUpload, \
    SyncNomenclaturesUpload, SyncNomenclaturesResultRead
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
    Получает результат сопоставления номенклатур по указанному идентификаторы задания.

    Args:
        job_id (str): Идентификатор задания.

    Returns:
        list[MappingNomenclaturesResultRead]: Список результатов сопоставления.
    """
    return nomenclature_model.get_all_jobs(job_id)


@router.post("", response_model=JobIdRead)
@version(1)
def upload_nomenclature(
    *,
    current_user: UserRead = Depends(get_current_user),
    nomenclatures: MappingNomenclaturesUpload
):
    """
    Запускает процесс сопоставления номенклатур.

    Args:
        nomenclatures (MappingNomenclaturesUpload): Номенклатуры для сопоставления.

    Returns:
        JobIdRead: Идентификатор задания.
    """
    return nomenclature_model.start_mapping(nomenclatures)


@router.post("/collection/{collection_name}")
@version(1)
def create_chroma_collection(
    *,
    current_user: UserRead = Depends(get_current_user),
    collection_name: str
):
    """
    Создает коллекцию Chroma.

    Args:
        collection_name (str): Название коллекции.

    Returns:
        Ничего
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
    Получает количество векторов в коллекции Chroma.

    Args:
        collection_name (str): Название коллекции.

    Returns:
        int: Длина коллекции.
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
    Удаляет коллекцию Chroma.

    Args:
        collection_name (str): Название коллекции.

    Returns:
        Ничего
    """
    return noms2embeddings_model.delete_chroma_collection(collection_name=collection_name)


@router.put("/collection")
@version(1)
def create_and_save_embeddings(
    *,
    current_user: UserRead = Depends(get_current_user),
    body: CreateAndSaveEmbeddingsUpload,
    background_tasks: BackgroundTasks
):
    """
    Создает и сохраняет вектора для всех номенклатур в ДВХ МСУ.

    Args:
        body (CreateAndSaveEmbeddingsUpload): Тело запроса.
        
    Returns:
        None
    """
    background_tasks.add_task(
        noms2embeddings_model.create_and_save_embeddings,
        nom_db_con_str=body.nom_db_con_str,
        table_name=body.table_name,
        top_n=body.top_n,
        order_by=body.order_by,
        offset=body.offset,
        chroma_collection_name=body.chroma_collection_name
    )
    return


@router.post("/synchronize", response_model=JobIdRead)
@version(1)
def synchronize_nomenclatures(
    *,
    body: SyncNomenclaturesUpload,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Синхронизирует номенклатуры в ДВХ МСУ и векторсторе.

    Args:
        body (SyncNomenclaturesUpload): Тело запроса.

    Returns:
        JobIdRead: Идентификатор задания.
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
        job_id (str): Идентификатор задания.

    Returns:
        SyncNomenclaturesResultRead: Результат синхронизации номенклатур.
    """
    return synchronize_nomenclatures_model.get_sync_nomenclatures_job_result(job_id)
