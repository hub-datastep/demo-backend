from chromadb import HttpClient, EmbeddingFunction
from chromadb.api.types import D
from fastembed.embedding import FlagEmbedding
from numpy import ndarray

chroma_client = HttpClient(host="localhost", port="8000")

COLLECTION__NAME = "nomenclature"


class NomenclatureEmbeddingFunction(EmbeddingFunction):

    def __call__(self, input: D) -> ndarray:
        embedding_model = FlagEmbedding(
            model_name="intfloat/multilingual-e5-large"
        )
        embeddings = list(embedding_model.query_embed([input]))[0]
        # return cast(Embeddings, embeddings)
        return embeddings


# Embeddable = Union[Documents, Images]
# D = TypeVar("D", bound=Embeddable, contravariant=True)
#
# class EmbeddingFunction(Protocol[D]):
#     def __call__(self, input: D) -> Embeddings:
#         ...


nomenclature_collection = chroma_client.create_collection(
    name=COLLECTION__NAME,
    # Default distance func is l2, but we use cosine
    metadata={"hnsw:space": "cosine"},
    embedding_function=NomenclatureEmbeddingFunction,
    get_or_create=True
)


def save_nom_embeddings(ids: list[str], nomenclatures: list[str], groups: list[str], embeddings: ...):
    nomenclature_collection.upsert(
        ids=ids,
        documents=nomenclatures,
        metadatas=[{"group": group} for group in groups],
        embeddings=embeddings,
    )


def get_similarity(nomenclature: str, group: str, count: int = 1):
    similarity = nomenclature_collection.query(
        query_texts=[nomenclature],
        where={"group": group},
        n_results=count,
        include=["documents", "metadatas"]
    )
    return similarity


if __name__ == "__main__":
    save_nom_embeddings(["1"], ["ggg"], ["hhh"], [[1, 2, 3]])
    test_s = get_similarity("ggg", "hhh")
    print(test_s)
    pass
