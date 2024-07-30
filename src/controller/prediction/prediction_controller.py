from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from middleware.mode_middleware import TenantMode, modes_required
from model.auth.auth_model import get_current_user
from model.prediction import datastep_pdf_model
from model.prediction.datastep_model import datastep_get_prediction
from repository.tenant import tenant_repository
from scheme.prediction.prediction_scheme import (
    DatabasePredictionQuery, DatabasePredictionRead,
    DocumentPredictionRead, DocumentPredictionQuery, PredictionQueryBase, KnowledgeBasePredictionRead
)
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.post("/assistant/prediction", response_model=DatabasePredictionRead)
@version(1)
@modes_required([TenantMode.DB])
async def get_database_prediction(
    query: DatabasePredictionQuery,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    """
    user_tenant_id = current_user.tenant_id
    current_user_tenant_db = tenant_repository.get_tenant_by_id(session, user_tenant_id)
    return await datastep_get_prediction(query, current_user_tenant_db, current_user.database_prediction_config)


@router.post("/chat_pdf/prediction", response_model=DocumentPredictionRead)
@version(1)
@modes_required([TenantMode.DOCS])
def get_document_prediction(
    body: DocumentPredictionQuery,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    """
    return datastep_pdf_model.get_prediction(session, body.query, body.file_id)


@router.post("/chat_knowledge_base/prediction", response_model=KnowledgeBasePredictionRead)
@version(1)
@modes_required([TenantMode.DOCS])
def get_knowledge_base_prediction(
    body: PredictionQueryBase,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    """
    return datastep_pdf_model.get_prediction_with_relevant_file(session, body.query, current_user.tenant_id)
