import re
from datetime import datetime

import joblib
from pandas import DataFrame, read_sql
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from tqdm import tqdm

tqdm.pandas()

_FILE_SEPARATOR = ";"
_TRAINING_FILE_NAME = "training_data.csv"


def _fetch_noms(db_con_str: str, table_name: str) -> DataFrame:
    st = f"""
        SELECT Наименование, Родитель
        FROM {table_name}
        WHERE ЭтоГруппа = 0
    """

    return read_sql(st, db_con_str)


def _fetch_groups(db_con_str: str, table_name: str) -> DataFrame:
    st = f"""
        SELECT DISTINCT Наименование, Ссылка
        FROM {table_name}
        WHERE ЭтоГруппа = 1
        AND (
            Наименование LIKE '__.__.__. %'
            OR Наименование LIKE '__.__. %'
        )
    """

    return read_sql(st, db_con_str)


def _has_child(db_con_str: str, table_name: str, group_name: str):
    group_numbs = group_name.split('. ')[0]

    st = f"""
        SELECT *
        FROM {table_name}
        WHERE Наименование LIKE '{group_numbs}.__. %'
        AND ЭтоГруппа = 1
    """
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


def _normalize_nom_name(text: str):
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
    narrow_group_noms = all_noms[all_noms['Родитель'].isin(no_child_groups['Ссылка'])]

    return DataFrame(narrow_group_noms)


def get_training_data(db_con_str: str, table_name: str) -> DataFrame:
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


def get_model_accuracy(classifier, vectorizer: CountVectorizer, x_test, y_test):
    y_pred = classifier.predict(vectorizer.transform(x_test))
    accuracy = accuracy_score(y_test, y_pred)
    return accuracy


def retrain_classifier(db_con_str: str, table_name: str):
    print("Getting training data...")
    training_data_df = get_training_data(db_con_str, table_name)
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

    accuracy = get_model_accuracy(
        classifier=classifier,
        vectorizer=vectorizer,
        x_test=x_test,
        y_test=y_test
    )

    files_date = datetime.now().date()
    vectorizer_file_name = f"vectorizer-{files_date}.pkl"
    classifier_file_name = f"linear-svc-model-{files_date}.pkl"

    joblib.dump(vectorizer, vectorizer_file_name)
    joblib.dump(classifier, classifier_file_name)


if __name__ == "__main__":
    from sshtunnel import SSHTunnelForwarder

    username = "wv-bleschunovd"
    jump_host_password = "$$R4Yt1w1nG52TBF"
    msu_db_password = "MRi9yJ6vPObQStZv"
    dbeaver_host = "192.168.0.238"

    reg_template1 = r"\d\d\.\d\d\.\d\d\.?.+"
    reg_template2 = r"\d\d\.\d\d\.?.+"

    print("Connecting to Jump Host...")
    jump_host_tunnel = SSHTunnelForwarder(
        ("192.168.0.20", 1984),
        ssh_username=username,
        ssh_password=jump_host_password,
        remote_bind_address=(dbeaver_host, 1984)
    )
    jump_host_tunnel.start()
    print("Connected.")
    jump_host_port = jump_host_tunnel.local_bind_port

    print("Connecting to MSU DB...")
    msu_db_tunnel = SSHTunnelForwarder(
        ("localhost", jump_host_port),
        ssh_username=username,
        ssh_password=msu_db_password,
        remote_bind_address=("srv-dwh", 1433)
    )
    msu_db_tunnel.start()
    print("Connected.")
    msu_db_port = str(msu_db_tunnel.local_bind_port)

    msu_db_connection_string = f"mssql+pyodbc://dwh_connector:Avt528796R001T@localhost:{msu_db_port}/dwh?driver=ODBC+Driver+17+for+SQL+Server"

    start_time = datetime.now()
    retrain_classifier(
        db_con_str=msu_db_connection_string,
        table_name="us.СправочникНоменклатура",
    )
    end_time = datetime.now()
    print(f"Script work time: {end_time - start_time}")
