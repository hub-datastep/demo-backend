from fastapi import HTTPException
from sqlmodel import Session

from repository.classifier import classifier_config_repository
from scheme.classifier.classifier_config_scheme import ClassifierConfigBase, ClassifierConfig


def get_classifier_config_by_user_id(
    session: Session,
    user_id: int,
) -> ClassifierConfig:
    classifier_config = classifier_config_repository.get_classifier_config_by_user_id(session, user_id)

    if classifier_config is None:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} does not have config for classifier.",
        )

    return classifier_config


def create_classifier_config(
    session: Session,
    config_params: ClassifierConfigBase,
    user_id: int,
) -> ClassifierConfig:
    classifier_config = classifier_config_repository.get_classifier_config_by_user_id(session, user_id)

    if classifier_config is not None:
        raise HTTPException(
            status_code=400,
            detail=f"User with ID {user_id} already have config for classifier.",
        )

    config = ClassifierConfig(
        **ClassifierConfigBase.dict(config_params),
        user_id=user_id,
    )

    classifier_config = classifier_config_repository.create_classifier_config(session, config)

    return classifier_config


def update_classifier_config_by_user_id(
    session: Session,
    config_params: ClassifierConfigBase,
    user_id: int,
) -> ClassifierConfig:
    classifier_config = get_classifier_config_by_user_id(session, user_id)

    classifier_config = ClassifierConfig.from_orm(
        obj=classifier_config,
        update=ClassifierConfigBase.dict(config_params, exclude_none=True),
    )

    classifier_config = classifier_config_repository.update_classifier_config(
        session=session,
        classifier_config=classifier_config,
    )

    return classifier_config


def delete_classifier_config_by_user_id(
    session: Session,
    user_id: int,
) -> None:
    classifier_config = get_classifier_config_by_user_id(session, user_id)
    classifier_config_repository.delete_classifier_config(session, classifier_config)
