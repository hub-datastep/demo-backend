import shutil

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents import Document
from langchain_openai import AzureOpenAIEmbeddings

from infra.env import env
from llm.chain.datastep_docs_chain import get_chain_for_docs
from llm.chain.datastep_knowledge_base_chain import get_chain_for_knowledge_base
from llm.chain.datastep_search_relevant_description_chain import get_chain_for_relevant_description
from scheme.file.file_scheme import KnowledgeBaseFile
from util.files_paths import get_file_folder_path

embeddingsDeployment = AzureOpenAIEmbeddings(
    deployment=env.AZURE_DEPLOYMENT_NAME_EMBEDDINGS,
)


def search_docs(storage_filename: str, query: str) -> tuple[str, int]:
    file_folder_path = get_file_folder_path(storage_filename)

    faiss_index = FAISS.load_local(
        f"{file_folder_path}/faiss",
        embeddingsDeployment,
        allow_dangerous_deserialization=True,
    )
    docs: list[Document] = faiss_index.similarity_search(query, k=7)
    doc_content = "".join([doc.page_content for doc in docs])
    # print("doc-content: " + doc_content)
    page: int = docs[0].metadata['page']
    # return docs[0]
    return doc_content, page


def search_for_knowledge_base(storage_filename: str, query: str) -> str:
    file_folder_path = get_file_folder_path(storage_filename)

    faiss_index = FAISS.load_local(
        f"{file_folder_path}/faiss",
        embeddingsDeployment,
        allow_dangerous_deserialization=True,
    )
    docs: list[Document] = faiss_index.similarity_search(query, k=7)
    doc_content = "".join([doc.page_content for doc in docs])
    # print("doc-content: " + doc_content)
    # return docs[0]
    return doc_content


def doc_query(storage_filename: str, query: str) -> tuple[str, int]:
    chain = get_chain_for_docs()
    # doc = search(storage_filename, query)
    doc_content, page = search_docs(storage_filename, query)
    response = chain.run(
        query=query,
        # document_content=doc.page_content,
        document_content=doc_content,
    )
    # page: int = doc.metadata['page']
    return response, page


def search_relevant_description(
    documents: list[KnowledgeBaseFile], query: str
) -> KnowledgeBaseFile | None:
    chain = get_chain_for_relevant_description()

    relevant_storage_filename = chain.run(
        documents=documents,
        query=query,
    )

    if relevant_storage_filename.lower() == "none":
        return None

    for doc in documents:
        if doc.storage_filename == relevant_storage_filename:
            return doc

    return None


def knowledge_base_query(storage_filename: str, query: str) -> tuple[str, int]:
    chain = get_chain_for_knowledge_base()
    doc_content = search_for_knowledge_base(storage_filename, query)
    response = chain.run(
        query=query,
        document_content=doc_content,
        document_name=storage_filename
    )
    return response


def save_document(storage_filename: str):
    file_folder_path = get_file_folder_path(storage_filename)
    file_path = f"{file_folder_path}/{storage_filename}"

    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    faiss_index = FAISS.from_documents(
        pages,
        embeddingsDeployment,
    )
    faiss_index.save_local(f"{file_folder_path}/faiss")


def split_text_into_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=[
            r'(?<=\n)(?=\d+\.\d+\s)',  # Разделение по пунктам списка типа 3.2, 3.3, и т.д.
            r'(?<=\n)(?=\d+\.\s)',  # Разделение по пунктам списка типа 1., 2., и т.д.
            r'\n\n+',  # Разделение по абзацам
        ],
        is_separator_regex=True,
        chunk_size=1000,
        chunk_overlap=0,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return [Document(page_content=chunk.strip()) for chunk in chunks if chunk.strip()]


def save_document_for_knowledge_base(storage_filename: str):
    file_folder_path = get_file_folder_path(storage_filename)
    file_path = f"{file_folder_path}/{storage_filename}"

    loader = PyPDFLoader(file_path)
    document_text = loader.load()
    full_text = " ".join([page.page_content for page in document_text])
    chunks = split_text_into_chunks(full_text)

    faiss_index = FAISS.from_documents(
        chunks,
        embeddingsDeployment,
    )
    faiss_index.save_local(f"{file_folder_path}/faiss")


def delete_document(storage_filename: str):
    file_folder_path = get_file_folder_path(storage_filename)
    shutil.rmtree(file_folder_path)
