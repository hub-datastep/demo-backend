import pathlib
import uuid

from langchain.schema.document import Document
from langchain.vectorstores import Chroma
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser
from langchain.prompts.chat import ChatPromptTemplate
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.output import LLMResult

from repository import file_upload_task_repository, file_repository

load_dotenv()
id_key = "doc_id"


class UpdateTaskHandler(BaseCallbackHandler):
    def __init__(self, task_id: int, last_progress: int, full_work):
        super()
        self.task_id = task_id
        self.last_progress = last_progress
        self.full_work = full_work

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: uuid.UUID,
        parent_run_id: uuid.UUID | None = None,
        **kwargs: any,
    ) -> any:
        file_upload_task_repository.increase_progress(self.task_id, self.last_progress + 1)
        self.last_progress += 1


def get_storage_path(source_id):
    return f"{pathlib.Path(__file__).parent.resolve()}/../../../data/{source_id}/multivector"


def get_doc_ids(docs):
    return [str(uuid.uuid4()) for _ in docs]


async def get_hypothetical_questions(file_id: int, docs):
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
        | ChatOpenAI(max_retries=0, model="gpt-3.5-turbo").bind(
                functions=functions,
                function_call={"name": "hypothetical_questions"}
        )
        | JsonKeyOutputFunctionsParser(key_name="questions")
    )
    task = file_upload_task_repository.create_task(file_id, len(docs))
    file_repository.update({"id": file_id}, {"file_upload_task_id": task.id})
    hypothetical_questions = await chain.abatch(docs, {
        "max_concurrency": 12,
        "callbacks": [UpdateTaskHandler(task.id, 0, len(docs))]}
    )
    file_upload_task_repository.update(task.id, {"status": "finished"})
    return hypothetical_questions


def get_docs(file_url):
    loader = PyPDFLoader(file_url)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000)
    return text_splitter.split_documents(docs)


def get_vectorstore(source_id):
    return Chroma(
        persist_directory=get_storage_path(source_id) + "/chroma",
        embedding_function=OpenAIEmbeddings()
    )


def save_store(source_id, docs, doc_ids):
    fs = LocalFileStore(get_storage_path(source_id) + "/documents")
    store = create_kv_docstore(fs)
    store.mset(list(zip(doc_ids, docs)))


def get_store(source_id):
    fs = LocalFileStore(get_storage_path(source_id) + "/documents")
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
        llm=ChatOpenAI(model_name="gpt-3.5-turbo-16k"),
        chain_type="stuff",
        retriever=retriever, chain_type_kwargs=chain_type_kwargs,
        return_source_documents=False
    )


async def save_chroma(file_id: int, source_id, docs, doc_ids):
    hypothetical_questions = await get_hypothetical_questions(file_id, docs)

    question_docs = []
    for i, question_list in enumerate(hypothetical_questions):
        question_docs.extend([Document(page_content=s, metadata={id_key: doc_ids[i]}) for s in question_list])

    Chroma.from_documents(
        question_docs,
        OpenAIEmbeddings(),
        persist_directory=get_storage_path(source_id) + "/chroma"
    )


async def save_document(file_id: int, source_id: str, file_url: str):
    docs = get_docs(file_url)
    doc_ids = get_doc_ids(docs)
    save_store(source_id, docs, doc_ids)
    await save_chroma(file_id, source_id, docs, doc_ids)
    file_repository.update({"id": file_id}, {"status": "active"})


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
