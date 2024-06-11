import shutil

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents import Document
from langchain_openai import AzureOpenAIEmbeddings

from datastep.chains.datastep_docs_chain import get_chain_for_docs
from datastep.chains.datastep_knowledge_base_chain import get_chain_for_knowledge_base
from datastep.chains.datastep_search_relevant_description_chain import get_chain_for_relevant_description
from infra.env import AZURE_DEPLOYMENT_NAME_EMBEDDINGS
from util.files_paths import get_file_folder_path


def search(storage_filename: str, query: str) -> tuple[str, int]:
    file_folder_path = get_file_folder_path(storage_filename)

    faiss_index = FAISS.load_local(
        f"{file_folder_path}/faiss",
        AzureOpenAIEmbeddings(
            azure_deployment=AZURE_DEPLOYMENT_NAME_EMBEDDINGS,
        ),
        allow_dangerous_deserialization=True,
    )
    docs: list[Document] = faiss_index.similarity_search(query, k=3)
    doc_content = "".join([doc.page_content for doc in docs])
    page: int = docs[0].metadata['page']
    # return docs[0]
    return doc_content, page

def doc_query(storage_filename: str, query: str) -> tuple[str, int]:
    chain = get_chain_for_docs()
    # doc = search(storage_filename, query)
    doc_content, page = search(storage_filename, query)
    response = chain.run(
        query=query,
        # document_content=doc.page_content,
        document_content=doc_content,
    )
    # page: int = doc.metadata['page']
    return response, page


def search_relevant_description(descriptions: list[dict], query: str, ) -> str:
    chain = get_chain_for_relevant_description()
    descriptions_str = "\n".join(
        [f"Filename: {file['filename']}, Description: {file['description']}" for file in descriptions])

    relevant_filename = chain.run(
        document_descriptions=descriptions_str,
        query=query
    )
    return relevant_filename


def knowledge_base_query(storage_filename: str, query: str) -> tuple[str, int]:
    chain = get_chain_for_knowledge_base()
    doc_content, page = search(storage_filename, query)
    response = chain.run(
        query=query,
        document_content=doc_content,
        document_name=storage_filename
    )
    return response, page


def save_document(storage_filename: str):
    file_folder_path = get_file_folder_path(storage_filename)
    file_path = f"{file_folder_path}/{storage_filename}"

    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    faiss_index = FAISS.from_documents(
        pages,
        AzureOpenAIEmbeddings(
            azure_deployment=AZURE_DEPLOYMENT_NAME_EMBEDDINGS,
        ),
    )
    faiss_index.save_local(f"{file_folder_path}/faiss")


def delete_document(storage_filename: str):
    file_folder_path = get_file_folder_path(storage_filename)
    shutil.rmtree(file_folder_path)
