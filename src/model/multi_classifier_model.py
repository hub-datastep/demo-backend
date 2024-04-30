import os
from pathlib import Path
from uuid import uuid4

import joblib
from fastapi import HTTPException, status
from pandas import DataFrame, read_sql
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sqlalchemy import text
from tqdm import tqdm

from infra.env import DATA_FOLDER_PATH
from infra.redis_queue import get_redis_queue, MAX_JOB_TIMEOUT, get_job, QueueName
from repository.classifier_version_repository import get_classifier_versions, delete_classifier_version_in_db, \
    get_classifier_version_by_model_id, create_classifier_version
from scheme.classifier_scheme import ClassifierVersion, ClassifierVersionRead, ClassifierRetrainingResult
from scheme.nomenclature_scheme import JobIdRead
from util.normalize_name import normalize_name

tqdm.pandas()

_FILE_SEPARATOR = ";"
_TRAINING_FILE_NAME = "training_data.csv"

_MAX_CLASSIFIERS_COUNT = 3


def _fetch_items(db_con_str: str, table_name: str) -> DataFrame:
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
    """)

    return read_sql(st, db_con_str)


def _has_child(db_con_str: str, table_name: str, group_id: str) -> bool:
    st = text(f"""
        SELECT *
        FROM {table_name}
        WHERE Родитель = '{group_id}'
        AND ЭтоГруппа = 1
    """)
    children = read_sql(st, db_con_str)

    return not children.empty


def _fetch_narrow_groups(db_con_str: str, table_name: str) -> DataFrame:
    print("Fetching groups...")
    groups = _fetch_groups(db_con_str, table_name)
    print(f"Count of groups: {len(groups)}")
    print(groups)

    print(f"Checking if groups have children...")
    narrow_groups = []
    for _, group in groups.iterrows():
        if not _has_child(db_con_str, table_name, group['Наименование']):
            narrow_groups.append(group)

    narrow_groups = DataFrame(narrow_groups)
    return narrow_groups


def _get_narrow_group_items(all_items: DataFrame, narrow_groups: DataFrame) -> DataFrame:
    # Return noms which Родитель in Ссылка of groups with no child
    narrow_group_items = all_items[all_items['Родитель'].isin(narrow_groups['Ссылка'])]

    return narrow_group_items


def _get_training_data(db_con_str: str, table_name: str) -> DataFrame:
    print("Fetching all items...")
    all_items = _fetch_items(db_con_str, table_name)
    print(f"Count of items: {len(all_items)}")
    print(all_items)

    print("Fetching narrow groups...")
    narrow_groups = _fetch_narrow_groups(db_con_str, table_name)
    print(f"Count of narrow groups: {len(narrow_groups)}")
    print(narrow_groups)

    print("Parsing narrow group items...")
    narrow_group_items = _get_narrow_group_items(all_items, narrow_groups)
    print(f"Count of narrow group items: {len(narrow_group_items)}")
    print(narrow_group_items)

    print("Normalizing narrow group items...")
    narrow_group_items['normalized'] = narrow_group_items['Наименование'].progress_apply(
        lambda x: normalize_name(x)
    )
    print(f"Count of normalized narrow group items: {len(narrow_group_items['normalized'])}")
    print(narrow_group_items['normalized'])

    # narrow_group_noms.to_csv(_TRAINING_FILE_NAME, sep=_FILE_SEPARATOR)
    return narrow_group_items


def _get_model_accuracy(classifier, vectorizer: CountVectorizer, x_test, y_test) -> float:
    y_pred = classifier.predict(vectorizer.transform(x_test))
    accuracy = accuracy_score(y_test, y_pred)
    return accuracy


def _dump_model(version_id: str, classifier, vectorizer: CountVectorizer) -> None:
    vectorizer_file_name = f"vectorizer_{version_id}.pkl"
    classifier_file_name = f"linear_svc_model_{version_id}.pkl"
    vectorizer_path = f"{DATA_FOLDER_PATH}/{vectorizer_file_name}"
    classifier_path = f"{DATA_FOLDER_PATH}/{classifier_file_name}"

    joblib.dump(classifier, classifier_path)
    joblib.dump(vectorizer, vectorizer_path)


def _save_classifier_version_to_db(classifier_version: ClassifierVersion) -> ClassifierVersionRead:
    classifier_version_db = create_classifier_version(classifier_version)
    saved_version = ClassifierVersionRead(
        model_id=classifier_version_db.id,
        description=classifier_version_db.description,
        created_at=classifier_version_db.created_at,
    )
    return saved_version


def _get_model_and_vectorizer_paths(model_id: str) -> tuple[Path, Path]:
    model_path = Path(f"{DATA_FOLDER_PATH}/linear_svc_model_{model_id}.pkl")
    vectorizer_path = Path(f"{DATA_FOLDER_PATH}/vectorizer_{model_id}.pkl")
    return model_path, vectorizer_path


def _delete_classifier_version_files(model_id: str) -> None:
    model_path, vectorizer_path = _get_model_and_vectorizer_paths(model_id)
    # Remove model file if exists
    if model_path.exists():
        os.remove(model_path)
    # Remove vectorizer file if exists
    if vectorizer_path.exists():
        os.remove(vectorizer_path)


def _retrain_classifier(db_con_str: str, table_name: str, model_description: str) -> ClassifierVersionRead:
    print("Getting training data...")
    training_data_df = _get_training_data(db_con_str, table_name)
    # training_data_df = read_csv(_TRAINING_FILE_NAME, sep=_FILE_SEPARATOR)
    print(f"Count of training data: {len(training_data_df)}")

    print("Training test split...")
    x_train, x_test, y_train, y_test = train_test_split(
        training_data_df['normalized'],
        training_data_df['Родитель'],
        random_state=0
    )
    print("Test split trained.")

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
        description=model_description,
        accuracy=accuracy,
    )

    print("Saving classifier version to db...")
    result = _save_classifier_version_to_db(classifier_version)
    print("Classifier version saved.")

    return result


def start_classifier_retraining(db_con_str: str, table_name: str, model_description: str) -> JobIdRead:
    queue = get_redis_queue(name=QueueName.RETRAINING)
    job = queue.enqueue(
        _retrain_classifier,
        db_con_str,
        table_name,
        model_description,
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
        retraining_result.result = job_result

    return retraining_result


def get_classifiers_list() -> list[ClassifierVersionRead]:
    classifiers_db_list = get_classifier_versions()
    classifier_versions_list = [ClassifierVersionRead(
        model_id=classifier.id,
        created_at=classifier.created_at,
    ) for classifier in classifiers_db_list]
    return classifier_versions_list


def delete_classifier_version(model_id: str):
    classifier_version = get_classifier_version_by_model_id(model_id)

    if classifier_version:
        _delete_classifier_version_files(model_id)
        delete_classifier_version_in_db(model_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classifier version with ID {model_id} not found."
        )
