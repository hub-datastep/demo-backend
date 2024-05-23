import os

import pandas as pd
from chromadb import HttpClient

from infra.chroma_store import FastembedChromaFunction
from infra.env import CHROMA_HOST, CHROMA_PORT
from model.feaure_extraction import extract_features
from util.feature_extraction_regex import regex_patterns


def create_chroma_collection(collection_name: str):
    chroma_client = HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    chroma_client.create_collection(name=collection_name, embedding_function=FastembedChromaFunction())


def delete_chroma_collection(collection_name: str):
    chroma_client = HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    chroma_client.delete_collection(collection_name)


def get_chroma_collection_length(collection_name: str) -> int:
    chroma_client = HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = chroma_client.get_collection(name=collection_name, embedding_function=FastembedChromaFunction())
    return collection.count()


def create_and_save_embeddings(
    nom_db_con_str: str,
    table_name: str,
    top_n: int,
    offset: int,
    order_by: str,
    chroma_collection_name: str
):
    def _fetch_noms() -> pd.DataFrame:
        st = f"SELECT * " \
             f"FROM {table_name} " \
             f"WHERE ЭтоГруппа = 0 " \
             f"ORDER BY {order_by} " \
             f"OFFSET {offset} ROWS " \
             f"FETCH NEXT {top_n} ROWS ONLY"

        return pd.read_sql(st, nom_db_con_str)

    def _save_embeddings(ids: list, documents: list, metadatas: list, batch_size: int = 256):
        chroma_client = HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        collection = chroma_client.get_collection(
            name=chroma_collection_name,
            embedding_function=FastembedChromaFunction()
        )

        for i in range(0, len(ids), batch_size):
            collection.add(
                documents=documents[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                ids=ids[i:i+batch_size]
            )

    df = _fetch_noms()
    print(f"Number of nomenclatures: {len(df)}")


    # Извлечение характеристик и добавление их в метаданные
    df_with_features = extract_features(df)

    # Разделяем сложную строку на несколько шагов
    metadatas = []
    for _, row in df_with_features.iterrows():
        # Извлечение значений регулярных выражений
        regex_values = row[regex_patterns.keys()].to_dict()
        # Преобразование ряда в словарь
        metadata = {"group": row["Родитель"]}
        # Объединение словарей
        metadata.update(regex_values)
        metadatas.append(metadata)

    ids = df_with_features["Ссылка"].to_list()
    documents = df_with_features["Наименование"].to_list()



    _save_embeddings(ids, documents, metadatas)

