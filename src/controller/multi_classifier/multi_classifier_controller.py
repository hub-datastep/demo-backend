from fastapi import APIRouter
from fastapi import Depends
from fastapi_versioning import version
from pydantic import BaseModel

from model import multi_classifier_model
from model.auth_model import get_current_user
from model.ner_model import get_ner_brand
from scheme.classifier_scheme import RetrainClassifierUpload, ClassifierRetrainingResult, ClassifierVersionRead, \
    ClassificationResult
from scheme.user_scheme import UserRead
from typing import List, Tuple

# Определение модели данных для результата NER
class NEREntity(BaseModel):
    text: str
    label: str


router = APIRouter()


@router.get("")
@version(1)
def get_multi_classifier_versions(
    *,
    current_user: UserRead = Depends(get_current_user),
) -> list[ClassifierVersionRead]:
    """
    Получает все версии обученных классификаторов.
    """
    return multi_classifier_model.get_classifiers_list()


@router.post("/retrain")
@version(1)
def retrain_multi_classifier(
    *,
    body: RetrainClassifierUpload,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Переобучает мульти-классификатор.
    """
    return multi_classifier_model.start_classifier_retraining(
        db_con_str=body.db_con_str,
        table_name=body.table_name,
        model_description=body.model_description,
    )


@router.get("/retrain/{job_id}")
@version(1)
def retrain_multi_classifier_result(
    job_id: str,
    current_user: UserRead = Depends(get_current_user),
) -> ClassifierRetrainingResult:
    """
    Получает результат переобучения мульти-классификатора.
    """
    return multi_classifier_model.get_retraining_job_result(job_id)


@router.delete("/{model_id}")
@version(1)
def delete_multi_classifier_by_id(
    *,
    current_user: UserRead = Depends(get_current_user),
    model_id: str
):
    """
    Удаляет версию классификатора с указанным идентификатором.
    """
    return multi_classifier_model.delete_classifier_version(model_id)


@router.post("/classification")
@version(1)
def start_classification(
    *,
    model_id: str,
    items: list[str],
    current_user: UserRead = Depends(get_current_user),
):
    """
    Классифицирует переданные элементы (ищет класс/группу каждого элемента в списке).
    """
    return multi_classifier_model.start_classification(
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
    return multi_classifier_model.get_classification_job_result(job_id)

@router.get("/ner")
@version(1)
def retrain_multi_classifier_result(
    current_user: UserRead = Depends(get_current_user),
) -> List[NEREntity]:
    """
    Получает результат ner.
    """
    entities = get_ner_brand('Составы-быстротвердеющий-DISPOMIX-PQ Procrete TR600')
    result = [NEREntity(text=ent[0], label=ent[1]) for ent in entities]
    return result