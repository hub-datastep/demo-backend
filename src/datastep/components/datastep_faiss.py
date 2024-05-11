import shutil

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents import Document
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from infra.env import AZURE_DEPLOYMENT_NAME_EMBEDDINGS, AZURE_DEPLOYMENT_NAME_DOCS_ASSISTANT
from util.files_paths import get_file_folder_path

DOCS_PROMPT_TEMPLATE = """
You are a lawyer specializing in the field of legal documents,
you understand various types of legal documentation like contracts, charters, regulations and others.
You clearly understand the contents of the documents and perfectly answer questions about them.
Determine the type and scope of the legal document to answer the question.
Highlight the key points and terms of the document to answer the question.

The content of the document can be solid text without spaces,
you need semantically place spaces between words.



Question:
{query}

Document content:
{document_content}

You must answer in Russian language.
Your answer:
"""


# Your answer should contain only part of the text from the document that contains the answer to the question.


def get_chain():
    # TODO: попробовать 3.5-instruct
    # llm = ChatOpenAI(
    #     temperature=0,
    #     model_name=DB_MODEL_NAME,
    #     openai_api_base=OPENAI_API_BASE
    # )
    llm = AzureChatOpenAI(
        azure_deployment=AZURE_DEPLOYMENT_NAME_DOCS_ASSISTANT,
        temperature=0,
        verbose=True,
    )

    prompt = PromptTemplate(
        template=DOCS_PROMPT_TEMPLATE,
        input_variables=["query", "document_content"]
    )

    return LLMChain(llm=llm, prompt=prompt)


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


def query(storage_filename: str, query: str) -> tuple[str, int]:
    chain = get_chain()
    # doc = search(storage_filename, query)
    doc_content, page = search(storage_filename, query)
    response = chain.run(
        query=query,
        # document_content=doc.page_content,
        document_content=doc_content,
    )
    # page: int = doc.metadata['page']
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
