from sqlmodel import Session, select

from scheme.classifier_config_scheme import ClassifierConfig


def get_classifier_config_by_user_id(session: Session, user_id: int) -> ClassifierConfig | None:
    st = select(ClassifierConfig) \
        .where(ClassifierConfig.user_id == user_id)

    classifier_config = session.exec(st).first()

    return classifier_config


def create_classifier_config(session: Session, classifier_config: ClassifierConfig) -> ClassifierConfig:
    session.add(classifier_config)
    session.commit()
    session.refresh(classifier_config)

    return classifier_config


def update_classifier_config(session: Session, classifier_config: ClassifierConfig) -> ClassifierConfig:
    new_classifier_config = session.merge(classifier_config)
    session.commit()

    return new_classifier_config


def delete_classifier_config(session: Session, classifier_config: ClassifierConfig) -> None:
    session.delete(classifier_config)
    session.commit()
