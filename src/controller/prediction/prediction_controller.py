from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model.prediction import datastep_pdf_model
from model.auth.auth_model import get_current_user
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
async def get_database_prediction(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    query: DatabasePredictionQuery
):
    """
    """
    user_tenant_id = current_user.tenants[0].id
    current_user_tenant_db = tenant_repository.get_tenant_by_id(session, user_tenant_id)
    return await datastep_get_prediction(query, current_user_tenant_db, current_user.database_prediction_config)


@router.post("/chat_pdf/prediction", response_model=DocumentPredictionRead)
@version(1)
def get_document_prediction(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    body: DocumentPredictionQuery
):
    """
    """
    return datastep_pdf_model.get_prediction(session, body.query, body.file_id)


@router.post("/chat_knowledge_base/prediction", response_model=KnowledgeBasePredictionRead)
@version(1)
def get_knowledge_base_prediction(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    body: PredictionQueryBase
):
    """
    """
    return datastep_pdf_model.get_prediction_with_relevant_file(session, body.query, current_user.tenants[0].id)
