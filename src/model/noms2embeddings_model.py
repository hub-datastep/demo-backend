import os

import chromadb
import pandas as pd

from infra.chroma_store import FastembedChromaFunction


def create_chroma_collection(collection_name: str):
    chroma_client = chromadb.HttpClient(host=os.getenv("CHROMA_HOST"), port=os.getenv("CHROMA_PORT"))
    chroma_client.create_collection(name=collection_name, embedding_function=FastembedChromaFunction())


def delete_chroma_collection(collection_name: str):
    chroma_client = chromadb.HttpClient(host=os.getenv("CHROMA_HOST"), port=os.getenv("CHROMA_PORT"))
    chroma_client.delete_collection(collection_name)


def get_chroma_collection_length(collection_name: str) -> int:
    chroma_client = chromadb.HttpClient(host=os.getenv("CHROMA_HOST"), port=os.getenv("CHROMA_PORT"))
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
             f"WHERE группа IS NOT NULL " \
             f"ORDER BY {order_by} " \
             f"OFFSET {offset} ROWS " \
             f"FETCH NEXT {top_n} ROWS ONLY"

        return pd.read_sql(st, nom_db_con_str)

    def _save_embeddings(ids: list, documents: list, metadatas: list, batch_size: int = 256):
        chroma_client = chromadb.HttpClient(host=os.getenv("CHROMA_HOST"), port=os.getenv("CHROMA_PORT"))
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

    ids = df["Ссылка"].to_list()
    documents = df["Наименование"].to_list()
    metadatas = [{"group": g} for g in df["группа"].to_list()]

    _save_embeddings(ids, documents, metadatas)

