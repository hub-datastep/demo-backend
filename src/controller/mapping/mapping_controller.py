from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model.auth.auth_model import get_current_user
from model.mapping import mapping_model
from repository.mapping import mapping_result_repository
from scheme.mapping.mapping_results_scheme import MappingResult
from scheme.mapping.mapping_scheme import MappingNomenclaturesUpload, MappingNomenclaturesResultRead
from scheme.task.task_scheme import JobIdRead
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("/history", response_model=list[MappingResult])
@version(1)
def get_saved_nomenclature_mapping_result_by_user_id(
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    Получает результаты сопоставления номенклатур через юзер айди.
    """
    return mapping_result_repository.get_nomenclature_results(session, current_user.id)


@router.post("", response_model=JobIdRead)
@version(1)
def start_nomenclature_mapping(
    body: MappingNomenclaturesUpload,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Запускает процесс сопоставления номенклатур.
    """
    tenant_id = current_user.tenant_id
    return mapping_model.start_mapping(
        nomenclatures=body.nomenclatures,
        most_similar_count=body.most_similar_count,
        chunk_size=body.chunk_size,
        classifier_config=current_user.classifier_config,
        tenant_id=tenant_id,
        is_use_brand_recognition=body.is_use_brand_recognition,
    )


@router.get("/{job_id}", response_model=list[MappingNomenclaturesResultRead])
@version(1)
def get_nomenclature_mapping_result(
    job_id: str,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Получает результат сопоставления номенклатур через указанный идентификатор задачи.
    """
    return mapping_model.get_all_jobs(job_id)
