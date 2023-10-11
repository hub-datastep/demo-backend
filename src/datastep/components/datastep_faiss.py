import pathlib

from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()


def save_document(source_id: str, file_url: str):
    loader = PyPDFLoader(file_url)
    pages = loader.load_and_split()
    faiss_index = FAISS.from_documents(pages, OpenAIEmbeddings())
    faiss_index.save_local(f"{pathlib.Path(__file__).parent.resolve()}/../../../data/{source_id}")


def search(source_id: str, query: str):
    faiss_index = FAISS.load_local(f"{pathlib.Path(__file__).parent.resolve()}/../../../data/{source_id}", OpenAIEmbeddings())
    doc = faiss_index.similarity_search(query, k=1)
    return doc[0]


if __name__ == "__main__":
    save_document("Dogovor_hozyaistvennyi_schet_razovyi.pdf", "https://jkhlwowgrekoqgvfruhq.supabase.co/storage/v1/object/public/files/Dogovor_hozyaistvennyi_schet_razovyi.pdf?t=2023-10-10T15%3A15%3A22.661Z")
