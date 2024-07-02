from pandas import DataFrame, read_sql
from sklearn.compose import make_column_selector, make_column_transformer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
from sqlalchemy import text
from tqdm import tqdm
from typing_extensions import deprecated

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


@deprecated("Not sure if this func is needed")
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


@deprecated("Not sure if this func is needed")
def _get_narrow_group_items(all_items: DataFrame, narrow_groups: DataFrame) -> DataFrame:
    # Return noms which "group" in "id" of groups with no child
    narrow_group_items = all_items[all_items['group'].isin(narrow_groups['name'])]

    return narrow_group_items


def get_training_data(
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
