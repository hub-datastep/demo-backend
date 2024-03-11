import os

import chromadb
import numpy as np
import pandas as pd

from tqdm import tqdm
from fastembed.embedding import TextEmbedding


def delete_chroma_collection(collection_name: str):
    chroma_client = chromadb.HttpClient(host=os.getenv("CHROMA_HOST"), port=os.getenv("CHROMA_PORT"))
    chroma_client.delete_collection(collection_name)


def get_chroma_collection_length(collection_name: str) -> int:
    chroma_client = chromadb.HttpClient(host=os.getenv("CHROMA_HOST"), port=os.getenv("CHROMA_PORT"))
    collection = chroma_client.get_or_create_collection(name=collection_name)
    return collection.count()


def create_and_save_embeddings(nom_db_con_str: str, collection_name: str, top_n: int = None):
    def get_embeddings(strings: list[str], total: int) -> list[np.ndarray]:
        embedding_model = TextEmbedding(
            model_name="intfloat/multilingual-e5-large"
        )
        strings = [f"query: {s}" for s in strings]
        result = [e.tolist() for e in tqdm(embedding_model.embed(strings), total=total)]
        return result

    def save_embeddings(df: pd.DataFrame):
        batch_size = 40000

        chroma_client = chromadb.HttpClient(host=os.getenv("CHROMA_HOST"), port=os.getenv("CHROMA_PORT"))
        collection = chroma_client.get_or_create_collection(name=collection_name)

        ids = df.id_1c.to_list()
        documents = df.Name.to_list()
        embeddings = df.embeddings.to_list()
        metadatas = [{"group": g} for g in df.NameParent1.to_list()]

        for i in range(0, len(ids), batch_size):
            collection.add(
                documents=documents[i:i+batch_size],
                embeddings=embeddings[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                ids=ids[i:i+batch_size]
            )

    st = "SELECT * FROM src1c.spr_nomenclature" if not top_n else f"SELECT TOP {top_n} * FROM src1c.spr_nomenclature"
    df = pd.read_sql(st, nom_db_con_str)
    print(f"Number of nomenclatures: {len(df)}")

    df["embeddings"] = get_embeddings(df.Name.to_list(), len(df))

    save_embeddings(df)


# if __name__ == "__main__":
#     tunnel = SSHTunnelForwarder(
#         ("***", "***"),
#         ssh_username="***",
#         ssh_password="***",
#         remote_bind_address=("***", "***")
#     )
#
#     tunnel.start()
#     port = tunnel.local_bind_port
#
#     tunnel2 = SSHTunnelForwarder(
#         ("***", "***"),
#         ssh_username="***",
#         ssh_password="***",
#         remote_bind_address=("***", "***")
#     )
#
#     tunnel2.start()
#     port2 = str(tunnel2.local_bind_port)
#
#     tunnel3 = SSHTunnelForwarder(
#         ("localhost", "***"),
#         ssh_username="***",
#         ssh_password="***",
#         remote_bind_address=("***", "***")
#     )
#
#     tunnel3.start()
#     port3 = str(tunnel3.local_bind_port)
#
#     connection_string = \
#         f"***"
#
#     os.environ["FASTEMBED_CACHE_PATH"] = "***"
#
#     delete_collection("***", port3, "nomenclature")
#     create_and_save_embeddings(connection_string, "***", port3, "***")
#     print(get_collection_length("***", port3, "***"))

