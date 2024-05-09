from fastapi import APIRouter
from fastapi import Depends
from fastapi_versioning import version

from model import multi_classifier_model
from model.auth_model import get_current_user
from scheme.classifier_scheme import RetrainClassifierUpload, ClassifierRetrainingResult, ClassifierVersionRead, \
    ClassificationResult
from scheme.user_scheme import UserRead

router = APIRouter()


@router.get("")
@version(1)
def get_multi_classifier_versions(
    *,
    current_user: UserRead = Depends(get_current_user),
) -> list[ClassifierVersionRead]:
    """
    Получает все версии обученных классификаторов

    Returns:
        list[ClassifierVersionRead]: Список обученных классификаторов
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
    Отсутствует какая-либо фильтрация. Рекомендуется использовать таблицы с хорошими данными.

    Args:
        body (RetrainClassifierUpload): Тело запроса.
            - db_con_str (str): Строка подключения к базе данных
            - table_name (str): Таблица, по которой классификатор будет обучаться
                                (указывается в виде: us.СправочникНоменклатура)
            - model_description (str): Описание классификатора (на чём обучен, для чего и т.п.)

    Returns:
        JobIdRead: Идентификатор задачи.
    """
    return multi_classifier_model.start_classifier_retraining(
        db_con_str=body.db_con_str,
        table_name=body.table_name,
        model_description=body.model_description,
    )


@router.get("/retrain/result")
@version(1)
def retrain_multi_classifier_result(
    *,
    current_user: UserRead = Depends(get_current_user),
    job_id: str
) -> ClassifierRetrainingResult:
    """
    Получает результат переобучения мульти-классификатора.

    Args:
        job_id (str): Идентификатор задачи.

    Returns:
        ClassifierRetrainingResult: Результат переобучения мульти-классификатора
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

    Args:
        model_id (str): Идентификатор модели классификатора
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
    Классифицирует переданные элементы (ищет класс/группу каждого элемента в списке)

    Args:
        model_id (str): Идентификатор классификатора
        items (list[str]): Список элементов (наименований), которые нужно классифицировать

    Returns:
        JobIdRead: Идентификатор задачи.
    """
    return multi_classifier_model.start_classification(
        items=items,
        model_id=model_id,
    )


@router.get("/classification/result")
@version(1)
def get_classification_result(
    *,
    current_user: UserRead = Depends(get_current_user),
    job_id: str
) -> ClassificationResult:
    """
    Получает результат классификации.

    Args:
        job_id (str): Идентификатор задачи

    Returns:
        ClassificationResult: Результат классификации
    """
    return multi_classifier_model.get_classification_job_result(job_id)
