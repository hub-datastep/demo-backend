from sqlmodel import Session, select, not_

from infra.database import engine
from scheme.classifier_scheme import ClassifierVersion


def get_classifier_versions():
    with Session(engine) as session:
        st = select(ClassifierVersion) \
            .where(not_(ClassifierVersion.is_deleted))
        result = session.exec(st).all()

    return list(result)


def get_classifier_version_by_model_id(model_id: str) -> ClassifierVersion | None:
    with Session(engine) as session:
        classifier_version = session.get(ClassifierVersion, model_id)

    return classifier_version


def delete_classifier_version_in_db(classifier_version: ClassifierVersion):
    # Soft delete classifier version in our postgres db
    with Session(engine) as session:
        classifier_version.is_deleted = True
        session.add(classifier_version)
        session.commit()
