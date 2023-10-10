from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain import PromptTemplate
from dotenv import load_dotenv

load_dotenv()


def save_document(source_id: str, file_url: str):
    loader = PyPDFLoader(file_url)
    pages = loader.load_and_split()
    faiss_index = FAISS.from_documents(pages, OpenAIEmbeddings())
    faiss_index.save_local(f"../../../data/{source_id}")


def search(source_id: str, query: str):
    faiss_index = FAISS.load_local(f"../../../data/{source_id}", OpenAIEmbeddings())
    doc = faiss_index.similarity_search(query, k=1)
    return doc[0]


if __name__ == "__main__":
    file_url = "https://jkhlwowgrekoqgvfruhq.supabase.co/storage/v1/object/public/files/a1d9b1427998cee7e4983c7ab194816e.pdf?t=2023-10-10T10%3A24%3A32.502Z"
    source_id = "123"
    save_document(source_id, file_url)
    print(search(source_id, "Выплата купона"))
