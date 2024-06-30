from fastapi import APIRouter, Depends
from fastapi_versioning import version

from model.auth.auth_model import get_current_user
from model.mapping import synchronize_model
from scheme.nomenclature.nomenclature_scheme import JobIdRead, SyncNomenclaturesUpload, SyncNomenclaturesResultRead
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.post("", response_model=JobIdRead)
@version(1)
def synchronize_nomenclatures(
    body: SyncNomenclaturesUpload,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Синхронизирует номенклатуры в БД и векторсторе за указанный период.
    """
    return synchronize_model.start_synchronizing_nomenclatures(
        nom_db_con_str=body.nom_db_con_str,
        chroma_collection_name=body.chroma_collection_name,
        sync_period=body.sync_period,
    )


@router.get("/{job_id}")
@version(1)
def synchronize_nomenclatures_result(
    job_id: str,
    current_user: UserRead = Depends(get_current_user),
) -> SyncNomenclaturesResultRead:
    """
    Получает результат синхронизации номенклатур в БД и векторсторе.
    """
    return synchronize_model.get_sync_nomenclatures_job_result(job_id)
