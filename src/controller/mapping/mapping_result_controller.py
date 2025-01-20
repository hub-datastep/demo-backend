from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from middleware.mode_middleware import TenantMode, modes_required
from model.auth.auth_model import get_current_user
from model.mapping.result import mapping_result_model, mapping_iteration_model
from repository.mapping import mapping_result_repository
from scheme.mapping.result.mapping_iteration_scheme import IterationWithResults
from scheme.mapping.result.mapping_result_scheme import (
    MappingResult,
    MappingResultUpdate,
)
from scheme.mapping.search_autocomplete_scheme import AutocompleteNomenclatureNameQuery
from scheme.user.user_scheme import UserRead

router = APIRouter()


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


@router.post("/similar_search", response_model=list[str])
@version(1)
@modes_required([TenantMode.CLASSIFIER])
def get_similar_nomenclatures_by_user_query(
    body: AutocompleteNomenclatureNameQuery,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    return mapping_result_model.get_similar_nomenclatures(body.query, current_user, session)


@router.put("/history", response_model=MappingResult)
@version(1)
@modes_required([TenantMode.CLASSIFIER])
def save_correct_nomenclature(
    body: MappingResultUpdate,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    return mapping_result_repository.save_correct_nomenclature(body, session)
