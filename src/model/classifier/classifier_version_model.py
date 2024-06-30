import os
from pathlib import Path

from fastapi import HTTPException, status

from infra.env import DATA_FOLDER_PATH
from repository.classifier.classifier_version_repository import get_classifier_versions, \
    delete_classifier_version_in_db, \
    get_classifier_version_by_model_id
from scheme.classifier.classifier_version_scheme import ClassifierVersionRead


def get_classifiers_list() -> list[ClassifierVersionRead]:
    classifiers_db_list = get_classifier_versions()
    classifier_versions_list = [ClassifierVersionRead(
        model_id=classifier.id,
        description=classifier.description,
        created_at=classifier.created_at,
    ) for classifier in classifiers_db_list]
    return classifier_versions_list


def get_model_path(model_id: str) -> str:
    model_path = f"{DATA_FOLDER_PATH}/model_{model_id}.pkl"
    return model_path


def _delete_classifier_version_files(model_id: str) -> None:
    model_path = get_model_path(model_id)
    # Remove model file if exists
    if Path(model_path).exists():
        os.remove(model_path)


def delete_classifier_version(model_id: str):
    classifier_version = get_classifier_version_by_model_id(model_id)

    if classifier_version:
        _delete_classifier_version_files(model_id)
        delete_classifier_version_in_db(classifier_version)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classifier version with ID {model_id} not found."
        )
