from fastapi import APIRouter, Depends
from fastapi_versioning import version

from middleware.mode_middleware import TenantMode, modes_required
from model.auth.auth_model import get_current_user
from model.mapping import mapping_model, mapping_cim_work_type_model
from scheme.mapping.mapping_scheme import (
    MappingNomenclaturesUpload,
    MappingNomenclaturesResultRead,
)
from scheme.mapping.result.mapping_result_scheme import (
    InputModel,
    MappedCimModel,
)
from scheme.task.task_scheme import JobIdRead
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.post("", response_model=JobIdRead)
@version(1)
@modes_required([TenantMode.CLASSIFIER])
def start_mapping_job(
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
    )


@router.get("/{job_id}", response_model=list[MappingNomenclaturesResultRead])
@version(1)
@modes_required([TenantMode.CLASSIFIER])
def get_mapping_job_result(
    job_id: str,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Получает результат сопоставления номенклатур через указанный идентификатор задачи.
    """
    return mapping_model.get_all_jobs(job_id)


@router.post("/cim_model_work_types", response_model=MappedCimModel)
@version(1)
def mapping_cim_model(
    body: InputModel,
):
    return mapping_cim_work_type_model.mapping_cim_model(body)
