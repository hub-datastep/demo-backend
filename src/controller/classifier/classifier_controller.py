from fastapi import APIRouter
from fastapi import Depends
from fastapi_versioning import version

from model.auth.auth_model import get_current_user
from model.classifier import classifier_model, classification_model
from scheme.classifier.classifier_scheme import RetrainClassifierUpload, ClassifierRetrainingResult, \
    ClassifierVersionRead, \
    ClassificationResult
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("")
@version(1)
def get_classifier_versions(current_user: UserRead = Depends(get_current_user)) -> list[ClassifierVersionRead]:
    """
    Получает все версии обученных классификаторов.
    """
    return classifier_model.get_classifiers_list()


@router.post("/retrain")
@version(1)
def retrain_classifier(
    body: RetrainClassifierUpload,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Переобучает мульти-классификатор.
    """
    return classifier_model.start_classifier_retraining(
        db_con_str=body.db_con_str,
        table_name=body.table_name,
        model_description=body.model_description,
        use_params=body.use_params,
    )


@router.get("/retrain/{job_id}")
@version(1)
def retrain_classifier_result(
    job_id: str,
    current_user: UserRead = Depends(get_current_user),
) -> ClassifierRetrainingResult:
    """
    Получает результат переобучения мульти-классификатора.
    """
    return classifier_model.get_retraining_job_result(job_id)


@router.delete("/{model_id}")
@version(1)
def delete_classifier_by_id(
    model_id: str,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Удаляет версию классификатора с указанным идентификатором.
    """
    return classifier_model.delete_classifier_version(model_id)


@router.post("/classification")
@version(1)
def start_classification(
    model_id: str,
    items: list[str],
    current_user: UserRead = Depends(get_current_user),
):
    """
    Классифицирует переданные элементы (ищет класс/группу каждого элемента в списке).
    """
    return classification_model.start_classification(
        items=items,
        model_id=model_id,
    )


@router.get("/classification/{job_id}")
@version(1)
def get_classification_result(
    job_id: str,
    current_user: UserRead = Depends(get_current_user),
) -> ClassificationResult:
    """
    Получает результат классификации.
    """
    return classification_model.get_classification_job_result(job_id)
