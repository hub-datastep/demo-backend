from fastapi import APIRouter
from fastapi import Depends
from fastapi_versioning import version

from model import multi_classifier_model
from model.auth_model import get_current_user
from scheme.classifier_scheme import RetrainClassifierUpload, ClassifierRetrainingResult, ClassifierVersionRead
from scheme.user_scheme import UserRead

router = APIRouter()


@router.get("")
@version(1)
def get_multi_classifier_versions(
    *,
    current_user: UserRead = Depends(get_current_user),
) -> list[ClassifierVersionRead]:
    return multi_classifier_model.get_classifiers_list()


@router.post("")
@version(1)
def retrain_multi_classifier(
    *,
    body: RetrainClassifierUpload,
    current_user: UserRead = Depends(get_current_user),
):
    return multi_classifier_model.start_classifier_retraining(
        db_con_str=body.db_con_str,
        table_name=body.table_name,
        model_description=body.model_description,
    )


@router.post("/result")
@version(1)
def retrain_multi_classifier_result(
    *,
    current_user: UserRead = Depends(get_current_user),
    job_id: str
) -> ClassifierRetrainingResult:
    return multi_classifier_model.get_retraining_job_result(job_id)


@router.delete("/{model_id}")
@version(1)
def delete_multi_classifier_by_id(
    *,
    current_user: UserRead = Depends(get_current_user),
    model_id: str
):
    return multi_classifier_model.delete_classifier_version(model_id)
