import uuid
from pathlib import Path

from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import RetrievalQA
from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import ChatPromptTemplate
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.schema import OutputParserException
from langchain.schema.document import Document
from langchain.schema.output import LLMResult
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from rq import get_current_job
from rq.job import Job

from infra.env import AZURE_DEPLOYMENT_NAME_SIMILAR_QUERIES, AZURE_DEPLOYMENT_NAME_EMBEDDINGS
from util.files_paths import get_file_folder_path

MULTIVECTOR_PROMPT_TEMPLATE = """
Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {query}
Answer in Russian:
"""

ID_KEY = "doc_id"


class UpdateTaskHandler(BaseCallbackHandler):
    def __init__(self, job: Job):
        super()
        self.current_progress = 0
        self.job = job

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: uuid.UUID,
        parent_run_id: uuid.UUID | None = None,
        **kwargs: any,
    ) -> any:
        self.current_progress += 1
        self.job.meta["progress"] = self.current_progress
        self.job.save_meta()


def get_doc_ids(docs):
    return [str(uuid.uuid4()) for _ in docs]


def get_hypothetical_questions(docs):
    functions = [
        {
            "name": "hypothetical_questions",
            "description": "Generate hypothetical questions",
            "parameters": {
                "type": "object",
                "properties": {
                    "questions": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                    },
                },
                "required": ["questions"]
            }
        }
    ]
    chain = (
        {"doc": lambda x: x.page_content}
        | ChatPromptTemplate.from_template(
        "Generate a list of 3 hypothetical questions in russian that the below document could be used to answer:\n\n{doc}"
    )
        # | ChatOpenAI(max_retries=6, model="gpt-3.5-turbo-1106", request_timeout=10,
        #              openai_api_base=OPENAI_API_BASE).bind(
        | AzureChatOpenAI(azure_deployment=AZURE_DEPLOYMENT_NAME_SIMILAR_QUERIES,
                          max_retries=6,
                          request_timeout=10).bind(
        functions=functions,
        function_call={"name": "hypothetical_questions"}
    )
        | JsonKeyOutputFunctionsParser(key_name="questions")
    )
    job = get_current_job()
    try:
        hypothetical_questions = chain.batch(docs, {
            "max_concurrency": 6,
            "callbacks": [UpdateTaskHandler(job)]}
                                             )
        return hypothetical_questions
    except OutputParserException:
        pass


def get_docs(file_path: Path):
    loader = PyPDFLoader(str(file_path))
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000)
    return text_splitter.split_documents(docs)


def get_vectorstore(storage_filename: str):
    file_folder_path = get_file_folder_path(storage_filename)
    chroma_folder_path = f"{file_folder_path}/multivector/chroma"

    return Chroma(
        persist_directory=chroma_folder_path,
        embedding_function=AzureOpenAIEmbeddings(
            azure_deployment=AZURE_DEPLOYMENT_NAME_EMBEDDINGS,
        ),
    )


def save_store(storage_filename: str, docs, doc_ids):
    file_folder_path = get_file_folder_path(storage_filename)
    chroma_folder_path = f"{file_folder_path}/multivector/documents/"

    fs = LocalFileStore(chroma_folder_path)
    store = create_kv_docstore(fs)
    store.mset(list(zip(doc_ids, docs)))


def get_store(storage_filename: str):
    file_folder_path = get_file_folder_path(storage_filename)
    chroma_folder_path = f"{file_folder_path}/multivector/documents/"

    fs = LocalFileStore(chroma_folder_path)
    return create_kv_docstore(fs)


def get_retriever(source_id):
    return MultiVectorRetriever(
        vectorstore=get_vectorstore(source_id),
        docstore=get_store(source_id),
        id_key=ID_KEY,
    )


def get_retriever_qa(retriever):
    prompt = PromptTemplate(
        template=MULTIVECTOR_PROMPT_TEMPLATE,
        input_variables=["context", "query"],
    )
    llm = AzureChatOpenAI(
        azure_deployment=AZURE_DEPLOYMENT_NAME_SIMILAR_QUERIES,
        max_retries=6,
        request_timeout=10,
    )
    chain_type_kwargs = {"prompt": prompt}
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs=chain_type_kwargs,
        return_source_documents=False
    )


def save_chroma(storage_filename: str, docs, doc_ids):
    hypothetical_questions = get_hypothetical_questions(docs)

    question_docs = []
    for i, question_list in enumerate(hypothetical_questions):
        question_docs.extend([Document(page_content=s, metadata={ID_KEY: doc_ids[i]}) for s in question_list])

    file_folder_path = get_file_folder_path(storage_filename)
    chroma_folder_path = file_folder_path / "multivector" / "chroma"

    Chroma.from_documents(
        question_docs,
        # OpenAIEmbeddings(),
        AzureOpenAIEmbeddings(
            azure_deployment=AZURE_DEPLOYMENT_NAME_EMBEDDINGS,
        ),
        persist_directory=str(chroma_folder_path)
    )


def save_document(storage_filename: str):
    file_folder_path = get_file_folder_path(storage_filename)

    file_path = Path(f"{file_folder_path}/{storage_filename}")
    docs = get_docs(file_path)
    doc_ids = get_doc_ids(docs)

    multivector_folder_path = f"{file_folder_path}/multivector"
    docs_folder_path = Path(f"{multivector_folder_path}/documents")
    if not docs_folder_path.is_dir():
        save_store(storage_filename, docs, doc_ids)

    # chroma_folder_path = Path(f"{multivector_folder_path}/chroma")
    # if not chroma_folder_path.is_dir():
    #     save_chroma(storage_filename, docs, doc_ids)


def query(source_id, query):
    retriever = get_retriever(source_id)
    qa = get_retriever_qa(retriever)
    response = qa.run(query=query)
    return response
