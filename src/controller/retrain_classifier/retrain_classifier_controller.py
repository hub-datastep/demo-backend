from fastapi import APIRouter
from fastapi import Depends
from fastapi_versioning import version

from model import retrain_classifier_model
from model.auth_model import get_current_user
from scheme.classifier_scheme import RetrainClassifierUpload, ClassifierRetrainingResult
from scheme.user_scheme import UserRead

router = APIRouter()


@router.post("/")
@version(1)
def retrain_classifier(
    *,
    body: RetrainClassifierUpload,
    current_user: UserRead = Depends(get_current_user),
):
    return retrain_classifier_model.start_classifier_retraining(
        db_con_str=body.db_con_str,
        table_name=body.table_name,
    )


@router.post("/result")
@version(1)
def retrain_classifier_result(
    *,
    current_user: UserRead = Depends(get_current_user),
    job_id: str
) -> ClassifierRetrainingResult:
    return retrain_classifier_model.get_retraining_job_result(job_id)
