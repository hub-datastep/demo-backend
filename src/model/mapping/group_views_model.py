import time
from pathlib import Path

from langchain.chains.llm import LLMChain
from pandas import DataFrame, read_excel

from datastep.chains.mapping_nomenclature_view_chain import get_chain
from infra.env import DATA_FOLDER_PATH

"""
Виды номенклатур определяются по внутренней группе (internal_group),
а не по НСИшной (group)
"""

GROUP_VIEWS_TABLE_PATH = f"{DATA_FOLDER_PATH}/levelgroup-group-views.xlsx"


def get_group_views(group: str, groups_view_df: DataFrame) -> str:
    # Проверяем, что файл с группами и их Видами существует локально
    if not Path(GROUP_VIEWS_TABLE_PATH).exists():
        raise Exception("Excel table with groups and views does not exists locally")

    # df = read_excel(GROUP_VIEWS_TABLE_PATH)

    # Ищем строки с Видами для нужной группы
    filtered_df = groups_view_df[groups_view_df['Внутренняя группа'] == group]

    # Соединяем все Виды в строку через запятую
    result = ", ".join(filtered_df['Вид'].astype(str))

    return result


def _get_nom_view(
    nom: DataFrame,
    views_chain: LLMChain,
    groups_view_df: DataFrame,
):
    # Timeout to not catch Rate Limit
    time.sleep(30)

    nom_group: str = nom['internal_group']

    views = get_group_views(
        group=nom_group,
        groups_view_df=groups_view_df,
    )
    nom_name: str = nom['nomenclature']

    nom_view = views_chain.run(
        nomenclature=nom_name,
        views=views,
    )

    return nom_view


def get_nomenclatures_views(nomenclatures: DataFrame):
    views_chain = get_chain()
    groups_view_df = read_excel(GROUP_VIEWS_TABLE_PATH)

    nomenclatures['view'] = nomenclatures.progress_apply(
        lambda nom: _get_nom_view(
            nom=nom,
            views_chain=views_chain,
            groups_view_df=groups_view_df,
        ),
        axis=1,
    )

    return nomenclatures
