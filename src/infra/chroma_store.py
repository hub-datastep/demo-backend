import os
from uuid import UUID

from chromadb import HttpClient
from chromadb.api.models.Collection import Collection

from chromadb import Documents, EmbeddingFunction, Embeddings
from fastembed.embedding import TextEmbedding
from scheme.nomenclature_scheme import SyncNomenclaturesChromaPatch, SyncOneNomenclatureDataRead
from tqdm import tqdm


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


def connect_to_chroma_collection(collection_name: str):
    chroma = HttpClient(host=os.getenv("CHROMA_HOST"), port=os.getenv("CHROMA_PORT"))
    collection = chroma.get_or_create_collection(
        name=collection_name,
        embedding_function=FastembedChromaFunction()
    )
    return collection


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


def drop_collection(collection_name: str):
    chroma = HttpClient(host=os.getenv("CHROMA_HOST"), port=os.getenv("CHROMA_PORT"))
    if collection_name in [c.name for c in chroma.list_collections()]:
        chroma.delete_collection(collection_name)


def create_collection(collection_name: str):
    connect_to_chroma_collection(collection_name)


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
    patch: list[SyncNomenclaturesChromaPatch]
) -> list[SyncNomenclaturesChromaPatch]:
    patched_list: list[SyncNomenclaturesChromaPatch] = []
    for elem in patch:
        # elem_id = elem.nomenclature_data.id
        # elem_nomenclature_name = elem.nomenclature_data.nomenclature_name
        # elem_group = elem.nomenclature_data.group
        # elem_action = elem.action

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

        patched_list.append(
            SyncNomenclaturesChromaPatch(
                nomenclature_data=SyncOneNomenclatureDataRead(
                    id=elem.nomenclature_data.id,
                    nomenclature_name=elem.nomenclature_data.nomenclature_name,
                    group=elem.nomenclature_data.group,
                ),
                action=elem.action
            )
        )
    return patched_list
