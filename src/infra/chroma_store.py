import os

from chromadb import HttpClient

from model.noms2embeddings_model import FastembedChromaFunction

chroma = HttpClient(host=os.getenv("CHROMA_HOST"), port=os.getenv("CHROMA_PORT"))
collection = chroma.get_or_create_collection(
    name="nomenclature",
    embedding_function=FastembedChromaFunction()
)


# TODO: rename func name to more semantic
def add_embeddings(
    documents: str | list[str],
    embeddings=None,
    ids: str | list[str] | None = None,
    metadatas=None,
):
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )


def delete_embeddings(ids: str | list[str]):
    collection.delete(ids=ids)


def update_embeddings(embeddings, ids: str | list[str]):
    collection.update(ids=ids, embeddings=embeddings)


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
