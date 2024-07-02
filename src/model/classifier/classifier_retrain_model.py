from uuid import uuid4

import joblib
from pandas import DataFrame, Series
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
from tqdm import tqdm

from infra.redis_queue import get_redis_queue, MAX_JOB_TIMEOUT, get_job, QueueName
from model.classifier.classifier_dataset_model import get_training_data
from model.classifier.classifier_version_model import get_model_path
from repository.classifier.classifier_version_repository import create_classifier_version
from scheme.classifier.classifier_version_scheme import ClassifierVersion, ClassifierVersionRead, \
    ClassifierRetrainingResult
from scheme.task.task_scheme import JobIdRead
from util.features_extraction import FEATURES_REGEX_PATTERNS

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


def _get_model_accuracy(classifier: Pipeline, x_test: DataFrame, y_test: Series) -> float:
    y_pred = classifier.predict(x_test)
    accuracy = accuracy_score(y_test, y_pred)
    return accuracy


def _dump_model(model_id: str, classifier) -> None:
    model_path = get_model_path(model_id)

    joblib.dump(classifier, model_path)


def _save_classifier_version_to_db(classifier_version: ClassifierVersion) -> ClassifierVersionRead:
    classifier_version_db = create_classifier_version(classifier_version)
    saved_version = ClassifierVersionRead(
        model_id=classifier_version_db.id,
        description=classifier_version_db.description,
        created_at=classifier_version_db.created_at,
    )
    return saved_version


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
    training_data_df = get_training_data(db_con_str, table_name, use_params)
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

    model_id = str(uuid4())

    job.meta['retrain_status'] = "Dumping model locally"
    job.save_meta()

    print("Dumping model locally...")
    _dump_model(
        model_id=model_id,
        classifier=classifier,
    )
    print("Model dumped.")

    classifier_version = ClassifierVersion(
        id=model_id,
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
