import os
import os
import re
from pathlib import Path
from uuid import uuid4

import joblib
from pandas import DataFrame, read_sql
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sqlalchemy import text
from sqlmodel import Session
from tqdm import tqdm

from infra.database import engine
from infra.redis_queue import get_redis_queue, MAX_JOB_TIMEOUT, get_job, QueueName
from repository.classifier_version_repository import _delete_classifier_version_in_db, _get_classifier_versions
from scheme.classifier_scheme import ClassifierVersion, ClassifierVersionRead, ClassifierRetrainingResult, \
    SyncClassifierVersionPatch
from scheme.nomenclature_scheme import JobIdRead

tqdm.pandas()

_FILE_SEPARATOR = ";"
_TRAINING_FILE_NAME = "training_data.csv"
DATA_FOLDER_PATH = os.getenv('DATA_FOLDER_PATH')

_MAX_CLASSIFIERS_COUNT = 3


def _fetch_noms(db_con_str: str, table_name: str) -> DataFrame:
    st = text(f"""
        SELECT Наименование, Родитель
        FROM {table_name}
        WHERE ЭтоГруппа = 0
    """)

    return read_sql(st, db_con_str)


def _fetch_groups(db_con_str: str, table_name: str) -> DataFrame:
    st = text(f"""
        SELECT DISTINCT Наименование, Ссылка
        FROM {table_name}
        WHERE ЭтоГруппа = 1
        AND (
            Наименование LIKE '__.__.__. %'
            OR Наименование LIKE '__.__. %'
        )
    """)

    return read_sql(st, db_con_str)


def _has_child(db_con_str: str, table_name: str, group_name: str) -> bool:
    group_numbs = group_name.split('. ')[0]

    st = text(f"""
        SELECT *
        FROM {table_name}
        WHERE Наименование LIKE '{group_numbs}.__. %'
        AND ЭтоГруппа = 1
    """)
    children = read_sql(st, db_con_str)

    return not children.empty


def _fetch_no_child_groups(db_con_str: str, table_name: str) -> DataFrame:
    print("Fetching groups...")
    groups = _fetch_groups(db_con_str, table_name)
    print(f"Count of groups: {len(groups)}")
    print(groups)

    print(f"Checking if groups have children...")
    no_child_groups = []
    for _, group in groups.iterrows():
        if not _has_child(db_con_str, table_name, group['Наименование']):
            no_child_groups.append(group)

    no_child_groups = DataFrame(no_child_groups)
    return no_child_groups


def _normalize_nom_name(text: str) -> str:
    text = text.lower()
    # deleting newlines and line-breaks
    text = re.sub(
        '\-\s\r\n\s{1,}|\-\s\r\n|\r\n',
        '',
        text
    )
    # deleting symbols
    text = re.sub(
        '[.,:;_%©?*,!@#$%^&()\d]|[+=]|[[]|[]]|[/]|"|\s{2,}|-',
        ' ',
        text
    )
    text = ' '.join(word for word in text.split() if len(word) > 2)

    return text


def _get_narrow_group_noms(all_noms: DataFrame, no_child_groups: DataFrame) -> DataFrame:
    # Return noms which Родитель in Ссылка of groups with no child
    print(f"res {no_child_groups}")
    print(f"ser {no_child_groups['Ссылка']}")
    narrow_group_noms = all_noms[all_noms['Родитель'].isin(no_child_groups['Ссылка'])]

    return narrow_group_noms


def _get_training_data(db_con_str: str, table_name: str) -> DataFrame:
    print("Fetching all noms...")
    all_noms = _fetch_noms(db_con_str, table_name)
    print(f"Count of noms: {len(all_noms)}")
    print(all_noms)

    print("Fetching no child groups...")
    no_child_groups = _fetch_no_child_groups(db_con_str, table_name)
    print(f"Count of no child groups: {len(no_child_groups)}")
    print(no_child_groups)

    print("Parsing narrow group noms...")
    narrow_group_noms = _get_narrow_group_noms(all_noms, no_child_groups)
    print(f"Count of narrow group noms: {len(narrow_group_noms)}")
    print(narrow_group_noms)

    print("Normalizing narrow group noms...")
    narrow_group_noms['normalized'] = narrow_group_noms['Наименование'].progress_apply(
        lambda x: _normalize_nom_name(x)
    )
    print(f"Count of normalized narrow group noms: {len(narrow_group_noms['normalized'])}")
    print(narrow_group_noms['normalized'])

    # narrow_group_noms.to_csv(_TRAINING_FILE_NAME, sep=_FILE_SEPARATOR)
    return narrow_group_noms


def _get_model_accuracy(classifier, vectorizer: CountVectorizer, x_test, y_test) -> float:
    y_pred = classifier.predict(vectorizer.transform(x_test))
    accuracy = accuracy_score(y_test, y_pred)
    return accuracy


def _dump_model(version_id: str, classifier, vectorizer: CountVectorizer) -> None:
    vectorizer_file_name = f"vectorizer_{version_id}.pkl"
    classifier_file_name = f"linear_svc_model_{version_id}.pkl"
    vectorizer_path = f"{os.getenv('DATA_FOLDER_PATH')}/{vectorizer_file_name}"
    classifier_path = f"{os.getenv('DATA_FOLDER_PATH')}/{classifier_file_name}"

    joblib.dump(classifier, classifier_path)
    joblib.dump(vectorizer, vectorizer_path)


def _save_classifier_version_to_db(classifier_version: ClassifierVersion) -> ClassifierVersionRead:
    # Save classifier version to our postgres db
    with Session(engine) as session:
        classifier_version_db = ClassifierVersion.from_orm(classifier_version)
        session.add(classifier_version_db)
        session.commit()
        session.refresh(classifier_version_db)

    saved_version = ClassifierVersionRead(
        model_id=classifier_version_db.id,
        created_at=classifier_version_db.created_at
    )
    return saved_version


def _get_model_and_vectorizer_paths(model_id: str) -> tuple[Path, Path]:
    model_path = Path(f"{DATA_FOLDER_PATH}/linear_svc_model_{model_id}.pkl")
    vectorizer_path = Path(f"{DATA_FOLDER_PATH}/vectorizer_{model_id}.pkl")
    return model_path, vectorizer_path


def _get_classifier_versions_sync_patch() -> list[SyncClassifierVersionPatch]:
    sync_patch: list[SyncClassifierVersionPatch] = []

    classifier_versions = _get_classifier_versions()
    if len(classifier_versions) > _MAX_CLASSIFIERS_COUNT:
        # First classifier versions with the greatest accuracy
        classifier_versions = sorted(classifier_versions, key=lambda x: x.accuracy, reverse=True)
        for classifier in classifier_versions[_MAX_CLASSIFIERS_COUNT:]:
            sync_patch.append(SyncClassifierVersionPatch(
                model_id=classifier.id,
                action="delete",
            ))

    return sync_patch


def _delete_classifier_version_files(model_id: str) -> None:
    model_path, vectorizer_path = _get_model_and_vectorizer_paths(model_id)
    # Remove model file if exists
    if model_path.exists():
        os.remove(model_path)
    # Remove vectorizer file if exists
    if vectorizer_path.exists():
        os.remove(vectorizer_path)


def _sync_classifier_versions(sync_patch: list[SyncClassifierVersionPatch]) -> None:
    for elem in sync_patch:
        if elem.action == "delete":
            _delete_classifier_version_in_db(model_id=elem.model_id)
            _delete_classifier_version_files(model_id=elem.model_id)


def _retrain_classifier(
    db_con_str: str,
    table_name: str
) -> tuple[ClassifierVersionRead, list[SyncClassifierVersionPatch]]:
    print("Getting training data...")
    training_data_df = _get_training_data(db_con_str, table_name)
    # training_data_df = read_csv(_TRAINING_FILE_NAME, sep=_FILE_SEPARATOR)
    print(f"Count of training data: {len(training_data_df)}")

    print("Training test split...")
    x_train, x_test, y_train, y_test = train_test_split(
        training_data_df['Наименование'],
        training_data_df['Родитель'],
        random_state=0
    )
    print("Training test split...")

    print("Fitting vectorizer...")
    vectorizer = CountVectorizer()
    x_train_counts = vectorizer.fit_transform(x_train.astype(str))
    print("Vectorizer is fitted.")

    print("Fitting TF-IDF transformer...")
    tfidf_transformer = TfidfTransformer()
    x_train_tfidf = tfidf_transformer.fit_transform(x_train_counts)
    print("Transformer is fitted.")

    print("Fitting classifier...")
    classifier = LinearSVC().fit(x_train_tfidf, y_train)
    print("Classifier is ready.")

    print("Getting model accuracy...")
    accuracy = _get_model_accuracy(
        classifier=classifier,
        vectorizer=vectorizer,
        x_test=x_test,
        y_test=y_test
    )
    print(f"Model accuracy: {accuracy}")

    version_id = str(uuid4())

    print("Dumping model locally...")
    _dump_model(
        version_id=version_id,
        classifier=classifier,
        vectorizer=vectorizer
    )
    print("Model dumped.")

    classifier_version = ClassifierVersion(
        id=version_id,
        accuracy=accuracy,
    )

    print("Saving classifier version to db...")
    result = _save_classifier_version_to_db(classifier_version)
    print("Classifier version saved.")

    print("Syncing classifier versions...")
    classifier_versions_sync_patch = _get_classifier_versions_sync_patch()
    _sync_classifier_versions(classifier_versions_sync_patch)
    print("Classifier version saved.")

    return result, classifier_versions_sync_patch


def start_classifier_retraining(db_con_str: str, table_name: str) -> JobIdRead:
    queue = get_redis_queue(name=QueueName.RETRAINING)
    job = queue.enqueue(
        _retrain_classifier,
        db_con_str,
        table_name,
        result_ttl=-1,
        job_timeout=MAX_JOB_TIMEOUT,
    )
    return JobIdRead(job_id=job.id)


def get_retraining_job_result(job_id: str) -> ClassifierRetrainingResult:
    job = get_job(job_id)

    retraining_result = ClassifierRetrainingResult(
        job_id=job_id,
        status=job.get_status(refresh=True)
    )

    job_result = job.return_value(refresh=True)
    if job_result is not None:
        result, changes = job_result
        retraining_result.result = result
        retraining_result.changes = changes

    return retraining_result


def get_classifiers_list() -> list[ClassifierVersionRead]:
    classifiers_db_list = _get_classifier_versions()
    classifier_versions_list = [ClassifierVersionRead(
        model_id=classifier.id,
        created_at=classifier.created_at,
    ) for classifier in classifiers_db_list]
    return classifier_versions_list
