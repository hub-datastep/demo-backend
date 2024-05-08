import shutil
from pathlib import Path

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from datastep.components.file_path_util import get_file_folder_path
from infra.env import AZURE_DEPLOYMENT_NAME_DB_ASSISTANT, AZURE_DEPLOYMENT_NAME_EMBEDDINGS

template = """
По данному тексту ответь на вопрос. Если для ответа на вопрос не хватает информации, напиши: Нет.

Вопрос:
{query}

Текст:
{text}
"""


def get_chain():
    # TODO: попробовать 3.5-instruct
    # llm = ChatOpenAI(
    #     temperature=0,
    #     model_name=DB_MODEL_NAME,
    #     openai_api_base=OPENAI_API_BASE
    # )
    llm = AzureChatOpenAI(
        azure_deployment=AZURE_DEPLOYMENT_NAME_DB_ASSISTANT,
        temperature=0,
        verbose=False,
    )

    prompt = PromptTemplate(
        template=template,
        input_variables=["query", "text"]
    )

    return LLMChain(llm=llm, prompt=prompt)


def save_document(storage_filename: str):
    file_folder_path = get_file_folder_path(storage_filename)
    file_path = Path(f"{file_folder_path}/{storage_filename}")

    loader = PyPDFLoader(str(file_path))
    pages = loader.load_and_split()
    faiss_index = FAISS.from_documents(
        pages,
        AzureOpenAIEmbeddings(
            azure_deployment=AZURE_DEPLOYMENT_NAME_EMBEDDINGS,
        ),
    )

    faiss_folder_path = file_folder_path / "faiss"
    faiss_index.save_local(str(faiss_folder_path))


def search(storage_filename: str, query: str):
    file_folder_path = get_file_folder_path(storage_filename)
    faiss_folder_path = file_folder_path / "faiss"

    faiss_index = FAISS.load_local(
        str(faiss_folder_path),
        AzureOpenAIEmbeddings(
            azure_deployment=AZURE_DEPLOYMENT_NAME_EMBEDDINGS,
        ),
        allow_dangerous_deserialization=True,
    )
    doc = faiss_index.similarity_search(query, k=1)
    return doc[0]


def query(source_id: str, query: str):
    chain = get_chain()
    doc = search(source_id, query)
    response = chain.run(
        query=query,
        text=doc.page_content
    )
    return doc.metadata["page"], response


def delete_document(source_id: str):
    store_file_path = get_file_folder_path(source_id)
    shutil.rmtree(store_file_path)
