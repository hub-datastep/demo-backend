import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
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
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from rq import get_current_job
from rq.job import Job

from datastep.components.file_path_util import get_file_folder_path

load_dotenv()
id_key = "doc_id"


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
        | ChatOpenAI(max_retries=6, model="gpt-3.5-turbo-1106", request_timeout=10, openai_api_base=os.getenv("OPENAI_API_BASE")).bind(
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
        # file_model.delete_file(file)
        # send_stop_job_command(Redis(), job.id)


def get_docs(file_path: Path):
    loader = PyPDFLoader(str(file_path))
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000)
    return text_splitter.split_documents(docs)


def get_vectorstore(storage_filename: str):
    file_folder_path = get_file_folder_path(storage_filename)
    chroma_folder_path = file_folder_path / "multivector" / "chroma"

    return Chroma(
        persist_directory=str(chroma_folder_path),
        embedding_function=OpenAIEmbeddings()
    )


def save_store(storage_filename: str, docs, doc_ids):
    # Split the original filename into name and extension
    file_folder_name, _ = os.path.splitext(storage_filename)
    chroma_folder_path = f"/app/data/{file_folder_name}/multivector/documents/"

    fs = LocalFileStore(chroma_folder_path)
    store = create_kv_docstore(fs)
    store.mset(list(zip(doc_ids, docs)))


def get_store(storage_filename: str):
    file_folder_name, _ = os.path.splitext(storage_filename)
    chroma_folder_path = f"/app/data/{file_folder_name}/multivector/documents/"

    fs = LocalFileStore(chroma_folder_path)
    return create_kv_docstore(fs)


def get_retriever(source_id):
    return MultiVectorRetriever(
        vectorstore=get_vectorstore(source_id),
        docstore=get_store(source_id),
        id_key=id_key,
    )


def get_retriever_qa(retriever):
    prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

    {context}

    Question: {question}
    Answer in Russian:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    chain_type_kwargs = {"prompt": PROMPT}
    return RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name="gpt-3.5-turbo-16k", openai_api_base=os.getenv("OPENAI_API_BASE")),
        chain_type="stuff",
        retriever=retriever, chain_type_kwargs=chain_type_kwargs,
        return_source_documents=False
    )


def save_chroma(storage_filename: str, docs, doc_ids):
    hypothetical_questions = get_hypothetical_questions(docs)

    question_docs = []
    for i, question_list in enumerate(hypothetical_questions):
        question_docs.extend([Document(page_content=s, metadata={id_key: doc_ids[i]}) for s in question_list])

    file_folder_path = get_file_folder_path(storage_filename)
    chroma_folder_path = file_folder_path / "multivector" / "chroma"

    Chroma.from_documents(
        question_docs,
        OpenAIEmbeddings(),
        persist_directory=str(chroma_folder_path)
    )


def save_document(storage_filename: str):
    file_folder_path = get_file_folder_path(storage_filename)
    chroma_folder_path = file_folder_path / "multivector"
    file_path = file_folder_path / storage_filename

    docs = get_docs(file_path)

    job = get_current_job()
    job.meta["progress"] = 0
    job.meta["full_work"] = len(docs)
    job.save_meta()

    doc_ids = get_doc_ids(docs)

    if not os.path.isdir(chroma_folder_path / "documents"):
        save_store(storage_filename, docs, doc_ids)

    if not os.path.isdir(chroma_folder_path / "chroma"):
        save_chroma(storage_filename, docs, doc_ids)


def query(source_id, query):
    retriever = get_retriever(source_id)
    qa = get_retriever_qa(retriever)
    response = qa.run(query)
    return response


if __name__ == "__main__":
    save_document(
        "Dog23012023_BI_3D_ispr_prava",
        "https://jkhlwowgrekoqgvfruhq.supabase.co/storage/v1/object/public/files/Dog23012023_BI_3D_ispr_prava.pdf"
    )
