from uuid import UUID

from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb import HttpClient
from chromadb.api.models.Collection import Collection
from fastembed.embedding import TextEmbedding
from rq.job import Job, get_current_job
from tqdm import tqdm

from infra.env import CHROMA_HOST, CHROMA_PORT
from scheme.nomenclature_scheme import SyncNomenclaturesChromaPatch


class FastembedChromaFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        embedding_model = TextEmbedding(
            model_name="intfloat/multilingual-e5-large"
        )
        strings = [f"query: {s}" for s in input]
        return [e.tolist() for e in tqdm(embedding_model.embed(strings), total=len(strings))]


def _cast_ids(ids: str | list[str] | UUID | list[UUID]):
    if isinstance(ids, list):
        return [str(i) for i in ids]
    else:
        return str(ids)


def get_chroma_client():
    chroma_client = HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    return chroma_client


def connect_to_chroma_collection(collection_name: str):
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        embedding_function=FastembedChromaFunction()
    )
    return collection


def create_collection(collection_name: str):
    chroma_client = get_chroma_client()
    chroma_client.create_collection(
        name=collection_name,
        embedding_function=FastembedChromaFunction()
    )


def delete_collection(collection_name: str):
    chroma_client = get_chroma_client()
    chroma_client.delete_collection(collection_name)


def get_collection_length(collection_name: str) -> int:
    collection = connect_to_chroma_collection(collection_name)
    return collection.count()


def add_embeddings(
    collection: Collection,
    ids: str | list[str] | UUID | list[UUID],
    documents: str | list[str],
    metadatas: dict | list[dict],
):
    ids = _cast_ids(ids)
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )


def delete_embeddings(collection: Collection, ids: str | list[str] | UUID | list[UUID]):
    ids = _cast_ids(ids)
    collection.delete(ids=ids)


def update_embeddings(
    collection: Collection,
    ids: str | list[str] | UUID | list[UUID],
    documents: str | list[str],
    metadatas: dict | list[dict],
):
    ids = _cast_ids(ids)
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


def update_collection_with_patch(
    collection: Collection,
    patch: list[SyncNomenclaturesChromaPatch],
    job: Job
) -> list[SyncNomenclaturesChromaPatch]:
    for elem in tqdm(patch):
        if elem.action == "delete":
            delete_embeddings(collection, ids=elem.nomenclature_data.id)
            print(f"Удалено: {elem.nomenclature_data.id}")

        elif elem.action == "create":
            add_embeddings(
                collection,
                ids=elem.nomenclature_data.id,
                documents=elem.nomenclature_data.nomenclature_name,
                metadatas={"group": str(elem.nomenclature_data.group)}
            )
            print(f"Добавлено: {elem.nomenclature_data.id}")

        elif elem.action == "update":
            update_embeddings(
                collection,
                ids=elem.nomenclature_data.id,
                documents=elem.nomenclature_data.nomenclature_name,
                metadatas={"group": str(elem.nomenclature_data.group)}
            )
            print(f"Обновлено: {elem.nomenclature_data.id}")

        job.meta["ready_count"] += 1
        job.save_meta()

    return patch


def create_embeddings_by_chunks(
    collection: Collection,
    ids: str | list[str] | UUID | list[UUID],
    documents: str | list[str],
    metadatas: dict | list[dict],
    chunk_size: int = 500,
    is_in_job: bool = True,
):
    if is_in_job:
        job = get_current_job()

    for i in range(0, len(ids), chunk_size):
        add_embeddings(
            collection=collection,
            ids=ids[i:i + chunk_size],
            documents=documents[i:i + chunk_size],
            metadatas=metadatas[i:i + chunk_size],
        )

        if is_in_job:
            job.meta['ready_count'] += 1
            job.save_meta()
