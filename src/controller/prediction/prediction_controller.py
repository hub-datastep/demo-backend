from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model import datastep_pdf_model
from model.datastep_model import datastep_get_prediction
from repository import user_repository
from scheme.prediction_scheme import (
    DatabasePredictionQuery, DatabasePredictionRead,
    DocumentPredictionRead, DocumentPredictionQuery
)

router = APIRouter()


@router.post("/assistant/prediction", response_model=DatabasePredictionRead)
@version(1)
async def get_database_prediction(*, session: Session = Depends(get_session), query: DatabasePredictionQuery):
    # return await datastep_get_prediction(query, current_user.tenant_id, current_user.database_prediction_config)
    current_user = user_repository.get_user_by_id(session, 1)
    last_tenant = [t for t in current_user.tenants if t.is_last is True][0]
    return await datastep_get_prediction(query, last_tenant, current_user.database_prediction_config)


@router.post("/chat_pdf/prediction", response_model=DocumentPredictionRead)
@version(1)
def get_document_prediction(*, session: Session = Depends(get_session), query: DocumentPredictionQuery):
    return datastep_pdf_model.get_prediction(query.filename, query.query)
