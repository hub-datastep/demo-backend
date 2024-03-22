import os

from chromadb import HttpClient
from chromadb.api.models.Collection import Collection

from model.noms2embeddings_model import FastembedChromaFunction
from scheme.nomenclature_scheme import SyncNomenclaturesPatch


def connect_to_chroma_collection(collection_name: str):
    chroma = HttpClient(host=os.getenv("CHROMA_HOST"), port=os.getenv("CHROMA_PORT"))
    collection = chroma.get_or_create_collection(
        name=collection_name,
        embedding_function=FastembedChromaFunction()
    )
    return collection


def add_embeddings(
    collection: Collection,
    ids: str | list[str],
    documents: str | list[str],
    metadatas: dict | list[dict],
):
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )


def delete_embeddings(collection: Collection, ids: str | list[str]):
    collection.delete(ids=ids)


def update_embeddings(
    collection: Collection,
    ids: str | list[str],
    documents: str | list[str],
    metadatas: dict | list[dict],
):
    collection.update(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )


def is_in_vectorstore(
    collection: Collection,
    ids: str | list[str],
):
    guid = collection.get(ids=ids)
    return len(guid['ids']) != 0


def update_collection_with_patch(collection: Collection, patch: list[SyncNomenclaturesPatch]):
    for elem in patch:
        if elem.action == "delete":
            delete_embeddings(collection, ids=elem.nomenclature_data.id)
            continue

        if elem.action == "create":
            add_embeddings(
                collection,
                ids=elem.nomenclature_data.id,
                documents=elem.nomenclature_data.nomenclature_name,
                metadatas={"group": elem.nomenclature_data.group}
            )
            continue

        if elem.action == "update":
            update_embeddings(
                collection,
                ids=elem.nomenclature_data.id,
                documents=elem.nomenclature_data.nomenclature_name,
                metadatas={"group": elem.nomenclature_data.group}
            )
            continue


if __name__ == "__main__":
    # load_dotenv()
    # tqdm.pandas()
    #
    # chroma = HttpClient(host=os.getenv("CHROMA_HOST"), port=os.getenv("CHROMA_PORT"))
    # collection = chroma.get_or_create_collection(name="nomenclature")
    #
    # df = pd.read_sql(
    #     "SELECT * FROM nomenclature WHERE embeddings IS NOT NULL",
    #     os.getenv("DB_CONNECTION_STRING")
    # )
    # df.embeddings = df.embeddings.progress_apply(ast.literal_eval)
    #
    # ids = [str(uuid4()) for _ in range(1, len(df) + 1)]
    # embeddings = df.embeddings.to_list()
    # documents = df.nomenclature.to_list()
    # metadatas = [{"group": g} for g in df.group.to_list()]
    #
    # print("1")
    # convert_sql_to_chroma(collection, documents[:40000], embeddings[:40000], metadatas[:40000], ids[:40000])
    # print("2")
    # convert_sql_to_chroma(collection, documents[40000:80000], embeddings[40000:80000], metadatas[40000:80000],
    #                       ids[40000:80000])
    # print("3")
    # convert_sql_to_chroma(collection, documents[80000:], embeddings[80000:], metadatas[80000:], ids[80000:])
    #
    # print(collection.count())
    pass
