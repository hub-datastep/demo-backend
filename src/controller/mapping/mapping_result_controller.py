from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from middleware.kafka_middleware import with_kafka_broker_connection
from middleware.mode_middleware import TenantMode, modes_required
from model.auth.auth_model import get_current_user
from model.mapping.result import mapping_result_model, mapping_iteration_model
from repository.mapping import mapping_iteration_repository
from scheme.file.utd_card_message_scheme import UTDCardOutputMessage
from scheme.mapping.result.mapping_iteration_scheme import (
    IterationWithResults,
    MappingIteration,
)
from scheme.mapping.result.mapping_result_scheme import (
    MappingResult,
    MappingResultUpdate,
    MappingResultsUpload,
)
from scheme.mapping.result.similar_nomenclature_search_scheme import (
    SimilarNomenclatureSearch,
    SimilarNomenclature,
)
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("/iteration", response_model=list[MappingIteration])
@version(1)
@modes_required([TenantMode.CLASSIFIER])
def get_iterations_list(
    iteration_id: str | None = None,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Получает все итерации маппинга.
    """
    return mapping_iteration_repository.get_iterations_list(iteration_id=iteration_id)


@router.get("/iteration/{iteration_id}", response_model=IterationWithResults)
@version(1)
@modes_required([TenantMode.CLASSIFIER])
def get_mapping_iteration_by_id(
    iteration_id: str,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Получает итерацию маппинга по ID с его результатами.
    """
    return mapping_iteration_model.get_iteration_by_id(iteration_id=iteration_id)


@router.post("/similar_nomenclatures", response_model=list[SimilarNomenclature])
@version(1)
@modes_required([TenantMode.CLASSIFIER])
def get_similar_nomenclatures(
    body: SimilarNomenclatureSearch,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    Получает список номенклатур, похожих на введённое значение.

    Номенклатуры ищутся в таблице, указанной в конфиге классификатора.
    - Параметр `nomenclatures_table_name`

    Обращение к таблице идёт по строке подключения, указанной у тенанта текущего юзера.
    - Параметр `db_uri`
    """
    return mapping_result_model.get_similar_nomenclatures(
        session=session,
        body=body,
        user=current_user,
    )


@router.put("/correct_nomenclature", response_model=list[MappingResult])
@version(1)
@modes_required([TenantMode.CLASSIFIER])
def update_mapping_results_list(
    body: MappingResultUpdate,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    Обновляет корректные номенклатуры в результатах маппинга.
    """
    return mapping_result_model.update_mapping_results_list(
        session=session,
        body=body,
    )


@router.post("/upload/kafka", response_model=UTDCardOutputMessage)
@version(1)
@modes_required([TenantMode.CLASSIFIER])
@with_kafka_broker_connection
async def upload_results_to_kafka(
    body: MappingResultsUpload,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    Отправляет проверенные результаты маппинга в Кафку Унистроя
    """
    return await mapping_result_model.upload_results_to_kafka(body=body)
