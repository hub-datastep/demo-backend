from fastapi import APIRouter, Depends
from fastapi_versioning import version

from model.auth.auth_model import get_current_user
from model.mapping import mapping_model
from scheme.mapping.mapping_scheme import MappingNomenclaturesUpload, MappingNomenclaturesResultRead
from scheme.task.task_scheme import JobIdRead
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.post("", response_model=JobIdRead)
@version(1)
def start_nomenclature_mapping(
    body: MappingNomenclaturesUpload,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Запускает процесс сопоставления номенклатур.
    """
    return mapping_model.start_mapping(
        nomenclatures=body.nomenclatures,
        most_similar_count=body.most_similar_count,
        chroma_collection_name=body.chroma_collection_name,
        chunk_size=body.chunk_size,
        model_id=body.model_id,
        use_params=body.use_params,
        classifier_config=current_user.classifier_config,
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
