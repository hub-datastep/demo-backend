from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model import datastep_pdf_model
from model.auth_model import get_current_user
from model.datastep_model import datastep_get_prediction
from repository import user_repository, tenant_repository
from scheme.prediction_scheme import (
    DatabasePredictionQuery, DatabasePredictionRead,
    DocumentPredictionRead, DocumentPredictionQuery
)
from scheme.user_scheme import UserRead

router = APIRouter()


@router.post("/assistant/prediction", response_model=DatabasePredictionRead)
@version(1)
async def get_database_prediction(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    query: DatabasePredictionQuery
):
    current_user_tenant_db = tenant_repository.get_tenant_by_id(session, current_user.tenants[0].id)
    return await datastep_get_prediction(query, current_user_tenant_db, current_user.database_prediction_config)


@router.post("/chat_pdf/prediction", response_model=DocumentPredictionRead)
@version(1)
def get_document_prediction(
    *,
    current_user: UserRead = Depends(get_current_user),
    query: DocumentPredictionQuery
):
    return datastep_pdf_model.get_prediction(query.filename, query.query)
