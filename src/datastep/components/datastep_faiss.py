import pathlib
import shutil

from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS

load_dotenv()


def get_store_file_path(source_id: str) -> str:
    return f"{pathlib.Path(__file__).parent.resolve()}/../../../data/{source_id}"


def save_document(source_id: str, file_url: str):
    loader = PyPDFLoader(file_url)
    pages = loader.load_and_split()
    faiss_index = FAISS.from_documents(pages, OpenAIEmbeddings())
    store_file_path = get_store_file_path(source_id)
    faiss_index.save_local(store_file_path)


def search(source_id: str, query: str):
    store_file_path = get_store_file_path(source_id)
    faiss_index = FAISS.load_local(
        store_file_path,
        OpenAIEmbeddings()
    )
    doc = faiss_index.similarity_search(query, k=1)
    return doc[0]


def delete_document(source_id: str):
    store_file_path = get_store_file_path(source_id)
    shutil.rmtree(store_file_path)


if __name__ == "__main__":
    save_document(
        "Dogovor_hozyaistvennyi_schet_razovyi.pdf",
        "https://jkhlwowgrekoqgvfruhq.supabase.co/storage/v1/object/public/files/Dogovor_hozyaistvennyi_schet_razovyi.pdf?t=2023-10-10T15%3A15%3A22.661Z"
    )