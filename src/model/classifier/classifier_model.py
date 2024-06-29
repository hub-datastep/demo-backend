import os
from pathlib import Path
from uuid import uuid4

import joblib
from fastapi import HTTPException, status
from pandas import DataFrame, read_sql, Series
from rq import get_current_job
from sklearn.compose import make_column_selector, make_column_transformer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.svm import LinearSVC
from sqlalchemy import text
from tqdm import tqdm

from infra.env import DATA_FOLDER_PATH
from infra.redis_queue import get_redis_queue, MAX_JOB_TIMEOUT, get_job, QueueName
from repository.classifier.classifier_version_repository import get_classifier_versions, delete_classifier_version_in_db, \
    get_classifier_version_by_model_id, create_classifier_version
from scheme.classifier.classifier_scheme import ClassifierVersion, ClassifierVersionRead, ClassifierRetrainingResult, \
    ClassificationResult, ClassificationResultItem
from scheme.nomenclature.nomenclature_scheme import JobIdRead
from util.features_extraction import FEATURES_REGEX_PATTERNS, extract_features
from util.normalize_name import normalize_name

tqdm.pandas()

_FILE_SEPARATOR = ";"
_TRAINING_FILE_NAME = "training_data.csv"

_MAX_CLASSIFIERS_COUNT = 3

_FEATURES = list(FEATURES_REGEX_PATTERNS.keys())

TRAINING_COLUMNS = [
    "normalized",
    *_FEATURES,
]

_text_transformer = make_pipeline(
    SimpleImputer(
        strategy="constant",
        fill_value="unknown",
    ),
    OneHotEncoder(
        handle_unknown="ignore",
    ),
)

_text_features = make_column_selector(dtype_include=object)

_preprocessor_with_params = make_column_transformer(
    (_text_transformer, _text_features),
)

_preprocessor_without_params = make_pipeline(
    CountVectorizer(),
    TfidfTransformer()
)


def _fetch_items(db_con_str: str, table_name: str) -> DataFrame:
    st = text(f"""
        SELECT "name", "group"
        FROM {table_name}
        WHERE "is_group" = FALSE
    """)

    return read_sql(st, db_con_str)


def _fetch_groups(db_con_str: str, table_name: str) -> DataFrame:
    st = text(f"""
        SELECT DISTINCT "name"
        FROM {table_name}
        WHERE "is_group" = TRUE
    """)

    return read_sql(st, db_con_str)


def _has_child(db_con_str: str, table_name: str, group: str) -> bool:
    st = text(f"""
        SELECT *
        FROM {table_name}
        WHERE "group" = '{group}'
        AND "is_group" = TRUE
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
        if not _has_child(db_con_str, table_name, group['name']):
            narrow_groups.append(group)

    narrow_groups = DataFrame(narrow_groups)
    return narrow_groups


def _get_narrow_group_items(all_items: DataFrame, narrow_groups: DataFrame) -> DataFrame:
    # Return noms which "group" in "id" of groups with no child
    narrow_group_items = all_items[all_items['group'].isin(narrow_groups['name'])]

    return narrow_group_items


def _get_training_data(
    db_con_str: str,
    table_name: str,
    use_params: bool,
) -> DataFrame:
    print("Fetching all items...")
    all_items = _fetch_items(db_con_str, table_name)
    print(f"Count of items: {len(all_items)}")
    print(all_items)

    # print("Fetching narrow groups...")
    # narrow_groups = _fetch_narrow_groups(db_con_str, table_name)
    # print(f"Count of narrow groups: {len(narrow_groups)}")
    # print(narrow_groups)
    #
    # print("Parsing narrow group items...")
    # narrow_group_items = _get_narrow_group_items(all_items, narrow_groups)
    # print(f"Count of narrow group items: {len(narrow_group_items)}")
    # print(narrow_group_items)

    narrow_group_items = all_items

    if use_params:
        print("Extracting items features...")
        narrow_group_items = extract_features(narrow_group_items)
        print("All features extracted.")
        print(narrow_group_items)

    print("Normalizing narrow group items...")
    narrow_group_items['normalized'] = narrow_group_items['name'].progress_apply(
        lambda x: normalize_name(x)
    )
    print(f"Count of normalized narrow group items: {len(narrow_group_items['normalized'])}")
    print(narrow_group_items['normalized'])

    # narrow_group_items.to_csv(_TRAINING_FILE_NAME, sep=_FILE_SEPARATOR)
    return narrow_group_items


def _get_model_accuracy(classifier: Pipeline, x_test: DataFrame, y_test: Series) -> float:
    y_pred = classifier.predict(x_test)
    accuracy = accuracy_score(y_test, y_pred)
    return accuracy


def _dump_model(version_id: str, classifier) -> None:
    classifier_file_name = f"model_{version_id}.pkl"
    classifier_path = f"{DATA_FOLDER_PATH}/{classifier_file_name}"

    joblib.dump(classifier, classifier_path)


def _save_classifier_version_to_db(classifier_version: ClassifierVersion) -> ClassifierVersionRead:
    classifier_version_db = create_classifier_version(classifier_version)
    saved_version = ClassifierVersionRead(
        model_id=classifier_version_db.id,
        description=classifier_version_db.description,
        created_at=classifier_version_db.created_at,
    )
    return saved_version


def _get_model_path(model_id: str) -> Path:
    model_path = Path(f"{DATA_FOLDER_PATH}/model_{model_id}.pkl")
    return model_path


def _delete_classifier_version_files(model_id: str) -> None:
    model_path = _get_model_path(model_id)
    # Remove model file if exists
    if model_path.exists():
        os.remove(model_path)


def _retrain_classifier(
    db_con_str: str,
    table_name: str,
    model_description: str,
    use_params: bool,
) -> ClassifierVersionRead:
    job = get_current_job()

    job.meta['retrain_status'] = "Getting training data"
    job.save_meta()

    print("Getting training data...")
    training_data_df = _get_training_data(db_con_str, table_name, use_params)
    # training_data_df = read_csv(_TRAINING_FILE_NAME, sep=_FILE_SEPARATOR)
    print(f"Count of training data: {len(training_data_df)}")

    # If without params -> use only "normalized" column
    if use_params:
        final_training_columns = TRAINING_COLUMNS
    else:
        final_training_columns = TRAINING_COLUMNS[0]

    final_training_data = training_data_df[final_training_columns]

    targets = training_data_df['group']

    print(f"Final training data length: {len(final_training_data)}")
    print(final_training_data)

    print(f"Final targets length: {len(targets)}")
    print(targets)

    job.meta['retrain_status'] = "Split training data"
    job.save_meta()

    x_train, x_test, y_train, y_test = train_test_split(
        final_training_data,
        targets,
        random_state=0,
    )

    print(f"Shapes of x_train, y_train: {x_train.shape} {y_train.shape}")
    print(f"Shapes of x_test, y_test: {x_test.shape} {y_test.shape}")

    if use_params:
        model = MLPClassifier()
        preprocessor = _preprocessor_with_params
    else:
        model = LinearSVC()
        preprocessor = _preprocessor_without_params

    classifier = make_pipeline(
        preprocessor,
        model,
    )

    job.meta['retrain_status'] = "Training classifier"
    job.save_meta()

    print("Fitting classifier...")
    classifier.fit(x_train, y_train)
    print("Classifier is ready.")

    job.meta['retrain_status'] = "Counting model accuracy"
    job.save_meta()

    print("Getting model accuracy...")
    accuracy = _get_model_accuracy(
        classifier=classifier,
        x_test=x_test,
        y_test=y_test,
    )
    print(f"Model accuracy: {accuracy}")

    version_id = str(uuid4())

    job.meta['retrain_status'] = "Dumping model locally"
    job.save_meta()

    print("Dumping model locally...")
    _dump_model(
        version_id=version_id,
        classifier=classifier,
    )
    print("Model dumped.")

    classifier_version = ClassifierVersion(
        id=version_id,
        description=model_description,
        accuracy=accuracy,
    )

    job.meta['retrain_status'] = "Saving classifier version to db"
    job.save_meta()

    print("Saving classifier version to db...")
    result = _save_classifier_version_to_db(classifier_version)
    print("Classifier version saved.")

    job.meta['retrain_status'] = "Done"
    job.save_meta()

    return result


def start_classifier_retraining(
    db_con_str: str,
    table_name: str,
    model_description: str,
    use_params: bool,
) -> JobIdRead:
    queue = get_redis_queue(name=QueueName.RETRAINING)
    job = queue.enqueue(
        _retrain_classifier,
        db_con_str,
        table_name,
        model_description,
        use_params,
        result_ttl=-1,
        job_timeout=MAX_JOB_TIMEOUT,
    )
    return JobIdRead(job_id=job.id)


def get_retraining_job_result(job_id: str) -> ClassifierRetrainingResult:
    job = get_job(job_id)
    job_status = job.get_status(refresh=True)
    job_meta = job.get_meta(refresh=True)

    retraining_result = ClassifierRetrainingResult(
        job_id=job_id,
        status=job_status,
        retrain_status=job_meta.get("retrain_status", None),
    )

    job_result = job.return_value(refresh=True)
    if job_result is not None:
        retraining_result.result = job_result

    return retraining_result


def get_classifiers_list() -> list[ClassifierVersionRead]:
    classifiers_db_list = get_classifier_versions()
    classifier_versions_list = [ClassifierVersionRead(
        model_id=classifier.id,
        description=classifier.description,
        created_at=classifier.created_at,
    ) for classifier in classifiers_db_list]
    return classifier_versions_list


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


def get_groups_by_items(items: list[str], model_id: str) -> list[ClassificationResultItem]:
    model = joblib.load(f"{DATA_FOLDER_PATH}/model_{model_id}.pkl")
    result: list[ClassificationResultItem] = []

    normalized_data = DataFrame({
        "names": [normalize_name(item) for item in items]
    })
    groups_ids = model.predict(normalized_data['names'])
    for item, group_id in zip(items, groups_ids):
        result.append(ClassificationResultItem(item=item, group_id=group_id))

    return result


def start_classification(items: list[str], model_id: str) -> JobIdRead:
    queue = get_redis_queue(name=QueueName.CLASSIFICATION)
    job = queue.enqueue(
        get_groups_by_items,
        items,
        model_id,
        result_ttl=-1,
        job_timeout=MAX_JOB_TIMEOUT,
    )
    return JobIdRead(job_id=job.id)


def get_classification_job_result(job_id: str) -> ClassificationResult:
    job = get_job(job_id)

    classification_result = ClassificationResult(
        job_id=job_id,
        status=job.get_status(refresh=True)
    )

    job_result = job.return_value(refresh=True)
    if job_result is not None:
        classification_result.result = job_result

    return classification_result
